import datetime
import os
import http.client
import pickle
import ssl
import threading
import json
import i18n

from datetime import datetime, timedelta
from flask import Flask
from werkzeug.exceptions import BadRequest
from classifiers.egvs.egvs_data_processor import process_data
from classifiers.egvs.egvs_classifier import train_model
from services import alexa_api_service, meal_recommendations_service
from services.notification_service import send_notification
from services.email_util_service import send_email
import services.meal_recommendations_service
from models.user import User
from flask import request
from models.recommendation_enums import *

import services.alexa_api_service

import pytz

# Creation of the Flask app
app = Flask(__name__)

os.environ['DEXCOM_URI'] = "sandbox-api.dexcom.com"
os.environ['GLUCODOC_EMAIL_PASSWORD'] = "glucodoc2016"

os.environ['HYPERGLYCEMIA_THRESHOLD'] = "180"
os.environ['HYPOGLYCEMIA_THRESHOLD'] = "70"

i18n.load_path.append('../i18n')


def get_database():
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb+srv://glucoDoc:glucoDoc@glucodoc.f8dds.mongodb.net/GlucoDoc?retryWrites=true&w=majority"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    from pymongo import MongoClient
    client = MongoClient(CONNECTION_STRING, ssl_cert_reqs=ssl.CERT_NONE)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['GlucoDoc']


gluco_doc_db = get_database()


def test():
    # gluco_doc_db = get_database()
    user_collection = gluco_doc_db['User']
    user_email = 'nativacu@gmail.com'
    user_query = {"user_email": user_email}
    result = user_collection.find(user_query)

    if any(u['user_email'] == user_email for u in result):
        result.rewind()
        user_dict = result.next()
        user = get_user_from_dict(user_dict)
        classified_model = pickle.loads(user.model)
        for i in range(7):
            for j in range(24):
                result = classified_model.predict([[str(i), str(j)]])
                print('weekday:' + str(i) + ' hour:' + str(j) + ' prediction:' + str(result))


@app.route('/')
def default():
    html_file = open("default_api_page.html", "r")
    thread = threading.Thread(target=test)
    thread.start()
    return html_file.read()


@app.route('/recommendationTemplate')
def recommendation_template():
    html_file = open("recommendation_templates/recommendation_page.html", "r")

    return html_file.read()


@app.route('/updateUser/<string:access_token>/<string:user_id>/<string:alexa_api_access_token>')
def update_user(access_token, user_id, alexa_api_access_token):
    # gluco_doc_db = get_database()
    user_collection = gluco_doc_db['User']
    user_locale = request.headers['locale']

    def train_m(user, is_new_user):
        conn = http.client.HTTPSConnection(os.getenv('DEXCOM_URI'))

        headers = {
            'authorization': "Bearer " + access_token
        }

        start_date = (datetime.now() - timedelta(91)).isoformat()
        end_date = (datetime.now() - timedelta(1)).isoformat()

        conn.request("GET", "/v2/users/self/egvs?startDate=" + start_date + "&endDate=" + end_date, headers=headers)

        res = conn.getresponse()
        json_data_string = res.read().decode("utf-8")

        user.model = pickle.dumps(train_model(process_data(json_data_string)))
        user.last_model_date = datetime.now()

        if is_new_user:
            user_collection.insert_one(user.__dict__)
        else:
            user_query = {"user_email": user.user_email}
            user_update = {"$set": user.__dict__}
            user_collection.update_one(user_query, user_update)

    def train_model_thread():

        user_email = alexa_api_service.get_user_email(alexa_api_access_token)
        user = User(user_id, None, None, user_email, user_locale)

        user_query = {"user_email": user_email}

        result = user_collection.find(user_query)

        if any(u['user_email'] == user_email for u in result):
            result.rewind()
            user_dict = result.next()

            if datetime.now() - user_dict['last_model_date'] >= timedelta(1):
                train_m(user, False)
        else:
            train_m(user, True)

    thread = threading.Thread(target=train_model_thread)
    thread.start()

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route(
    '/updateUserProfile/<string:alexa_api_access_token>/<string:sex>/<string:weight>/<string:height_m>/<string:age>',
    methods=['POST', 'GET'])
def update_user_personal_data(alexa_api_access_token, sex, weight, height_m, age):
    def update_profile():
        # gluco_doc_db = get_database()
        user_collection = gluco_doc_db['User']
        user_email = alexa_api_service.get_user_email(alexa_api_access_token)
        user_query = {"user_email": user_email}
        result = user_collection.find(user_query)
        edited = False

        if any(u['user_email'] == user_email for u in result):
            result.rewind()
            user = get_user_from_dict(result.next())
            if sex != 'None':
                user.sex = Sex.MALE.value if sex == 'male' else Sex.FEMALE.value
                edited = True
            if weight != 'None':
                user.weight = float(weight)
                edited = True
            if height_m != 'None':
                user.height_m = float(height_m)
                user.height_cm = float(height_m) * 100
                edited = True
            if age != 'None':
                user.age = int(age)
                edited = True
            user.activity_factor = ActivityFactor.HARD.value
            if edited:
                user.profile_modification_date = datetime.now()
                user_update = {"$set": user.__dict__}
                user_collection.update_one(user_query, user_update)

    # else:
    #     return json.dumps({'success': False, 'error_message': 'Could not find user'}), 404, {
    #         'ContentType': 'application/json'}

    thread = threading.Thread(target=update_profile)
    thread.start()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/getRecommendations', methods=['GET'])
@app.route('/getRecommendations/<string:meal_type>', methods=['GET'])
def get_meal_recommendations(meal_type=None):

    user_collection = gluco_doc_db['User']
    user_email = request.headers['user_email']
    user_query = {"user_email": user_email}
    result = user_collection.find(user_query)
    user_locale = str(request.headers['locale'])
    print(request.headers['user_email'])
    if any(u['user_email'] == user_email for u in result):
        result.rewind()
        user_dict = result.next()
        user = get_user_from_dict(user_dict)
        timezone_time = ''

        i18n.set('filename_format', user_locale + '.json')
        i18n.set('skip_locale_root_data', True)
        if meal_type is None:
            user_timezone_name = str(request.headers['timezone'])
            time_zone = pytz.timezone(user_timezone_name)
            timezone_time = datetime.now(time_zone).time().hour
        else:
            if meal_type == 'breakfast' or meal_type == 'desayuno':
                timezone_time = 7
            elif meal_type == 'lunch' or meal_type == 'almuerzo':
                timezone_time = 15
            else:
                timezone_time = 20

        if user.sex is not None and user.weight and user.height_cm and user.age:
            recommendations, distances = meal_recommendations_service.get_meal_recommendation_list(user.sex,
                                                                                                   user.weight,
                                                                                                   user.height_cm,
                                                                                                   user.age,
                                                                                                   user.activity_factor,
                                                                                                   int(timezone_time))

            meal_type = ''

            if int(timezone_time) < 12:
                meal_type = i18n.t("main.meal_recommendation.breakfast")
            elif 11 < int(timezone_time) < 18:
                meal_type = i18n.t("main.meal_recommendation.lunch")
            else:
                meal_type = i18n.t("main.meal_recommendation.dinner")

            return json.dumps({'success': True, 'recommendations': recommendations, 'meal_type': meal_type}), 200, {
                'ContentType': 'application/json'}
        else:
            return json.dumps({'success': False,
                               'error_message': i18n.t("main.meal_recommendation.incompleteProfile")}), 412, {
                       'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False, 'error_message': i18n.t("main.meal_recommendation.userNotFound")}), 404, {
            'ContentType': 'application/json'}


@app.route('/prediction/<string:weekday>/<string:time>/<string:alexa_api_access_token>', methods=['POST', 'GET'])
def date_time_prediction(weekday, time, alexa_api_access_token):
    # gluco_doc_db = get_database()
    user_collection = gluco_doc_db['User']
    user_email = alexa_api_service.get_user_email(alexa_api_access_token)
    user_query = {"user_email": user_email}
    result = user_collection.find(user_query)

    if any(u['user_email'] == user_email for u in result):
        result.rewind()
        user_dict = result.next()
        user = get_user_from_dict(user_dict)

        weekday_number = int(weekday)
        time_number = int(time)
        if weekday_number < 0 or weekday_number > 7:
            raise BadRequest('Weekday (' + weekday + ') out of range')
        if time_number < 0 or time_number > 24:
            raise BadRequest('Time (' + time + ') out of range')

        time = time[1] if len(time) > 1 and time[0] == 0 else time

        classified_model = pickle.loads(user.model)
        result = classified_model.predict([[str(weekday), str(time)]])

        return {
            'prediction': result[0],
            'training_model': False,
            'thresholds': {
                'hypoglycemia': os.getenv('HYPOGLYCEMIA_THRESHOLD'),
                'hyperglycemia': os.getenv('HYPERGLYCEMIA_THRESHOLD'),
            }
        }
    else:
        return {
            'prediction': None,
            'training_model': True
        }


# Endpoint used for testing
@app.route('/glucoseNotifications/<string:state>', methods=['POST', 'GET'])
def send_notifications_params(state):
    send_notifications(state)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/glucoseNotifications', methods=['POST', 'GET'])
def send_notifications(state=None):
    def notification_thread():

        # gluco_doc_db = get_database()
        user_collection = gluco_doc_db['User']
        cursor = user_collection.find({})

        for user_dict in cursor:

            user = get_user_from_dict(user_dict)
            i18n.set('filename_format', 'es-US' + '.json')
            i18n.set('skip_locale_root_data', True)
            classified_model = pickle.loads(user.model)
            result = None

            if state is not None:
                result = [str(state)]
            else:
                result = classified_model.predict([[str(datetime.now().weekday()), str(datetime.now().hour)]])

            if result[0] == "hypoglycemia" or result[0] == "hyperglycemia":
                i18n.set('filename_format', user.locale + '.json')
                i18n.set('skip_locale_root_data', True)
                send_email(user.user_email, i18n.t("main.glucose_email.subject"), i18n.t("main.glucose_email.body")
                           .format(i18n.t("main.glucose_email." + result[0])) + ".")
                send_notification(user.user_id)

    th = threading.Thread(target=notification_thread)
    th.start()

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/sendRecommendationEmail/<string:alexa_api_access_token>/<string:meal_id>', methods=['POST', 'GET'])
def send_recommendation_email(alexa_api_access_token, meal_id):
    def send_recommendation():
        # gluco_doc_db = get_database()
        user_collection = gluco_doc_db['User']
        user_email = alexa_api_service.get_user_email(alexa_api_access_token)
        user_query = {"user_email": user_email}
        result = user_collection.find(user_query)

        if any(u['user_email'] == user_email for u in result):
            result.rewind()
            user_dict = result.next()
            user = get_user_from_dict(user_dict)
            html_message = meal_recommendations_service.generate_recommendation_email_content(meal_id, user)
            date = datetime.now().date()
            send_email(user_email, "Your Meal Details (" + str(date) + ")", html_message, 'html')

    thread = threading.Thread(target=send_recommendation)
    thread.start()
    # html_message = generate_recommendation_email_content(meal_id)

    # return html_message, 200, {'ContentType': 'text/html'}
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/trainMealModel', methods=['GET'])
def train_meal_model_controller():
    meal_recommendations_service.train_meal_model()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return e, 400


def get_user_from_dict(user_dict):
    return User(user_dict['user_id'], user_dict['model'], user_dict['last_model_date'], user_dict['user_email'],
                user_dict['locale'], user_dict['sex'], user_dict['weight'], user_dict['height_m'],
                user_dict['height_cm'], user_dict['activity_factor'], user_dict['profile_modification_date'],
                user_dict["age"])


# WIP
def update_locale(locale, user_email, gluco_doc_db):
    user_collection = gluco_doc_db['User']

    user_query = {"user_email": user_email}
    result = user_collection.find(user_query)
    if any(u['user_email'] == user_email for u in result):
        result.rewind()
        user_dict = result.next()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
