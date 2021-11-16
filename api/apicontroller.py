import datetime
import os
import http.client
import pickle
import ssl
import threading
import json
import i18n
import pandas as pd

from datetime import datetime, timedelta
from flask import Flask
from werkzeug.exceptions import BadRequest
from classifiers.egvs.egvs_data_processor import process_data
from classifiers.egvs.egvs_classifier import train_model
from services.notification_service import send_notification
from services.email_util_service import get_user_email, send_email
from services.meal_recommendations_service import get_meal_recommendation_list
from models.user import User
from flask import request
from models.recommendation_enums import *

# Creation of the Flask app
app = Flask(__name__)

os.environ['DEXCOM_URI'] = "sandbox-api.dexcom.com"
os.environ['GLUCODOC_EMAIL_PASSWORD'] = "glucodoc2016"

os.environ['HYPERGLYCEMIA_THRESHOLD'] = "180"
os.environ['HYPOGLYCEMIA_THRESHOLD'] = "70"

i18n.load_path.append('../i18n')


# i18n.set('filename_format', locale + '.json')
# i18n.set('skip_locale_root_data', True)


@app.route('/')
def default():
    html_file = open("default_api_page.html", "r")
    return html_file.read()


@app.route('/updateUser/<string:access_token>/<string:user_id>/<string:alexa_api_access_token>')
def update_user(access_token, user_id, alexa_api_access_token):
    gluco_doc_db = get_database()
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

        user_email = get_user_email(alexa_api_access_token)
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

    th = threading.Thread(target=train_model_thread)
    th.start()

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/updateUser/<string:alexa_api_access_token>/<string:sex>/<string:weight>/<string:height_m>/<string:age>',
           methods=['POST', 'GET'])
def update_user_personal_data(alexa_api_access_token, sex, weight, height_m, age):
    gluco_doc_db = get_database()
    user_collection = gluco_doc_db['User']
    user_email = get_user_email(alexa_api_access_token)
    user_query = {"user_email": user_email}
    result = user_collection.find(user_query)
    edited = False

    if any(u['user_email'] == user_email for u in result):
        result.rewind()
        user = get_user_from_dict(result.next())
        if sex != 'None':
            user.sex = Sex.MALE.value if sex == 'male' else user.sex == Sex.FEMALE.value
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
        user.activity_factor = ActivityFactor.SEDENTARY.value
        if edited:
            user.profile_modification_date = datetime.now()
            user_update = {"$set": user.__dict__}
            user_collection.update_one(user_query, user_update)
    else:
        return json.dumps({'success': False, 'error_message': 'Could not find user'}), 404, {
            'ContentType': 'application/json'}

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/getRecommendations/<string:alexa_api_access_token>', methods=['POST', 'GET'])
def get_meal_recommendations(alexa_api_access_token):
    gluco_doc_db = get_database()
    user_collection = gluco_doc_db['User']
    user_email = get_user_email(alexa_api_access_token)
    user_query = {"user_email": user_email}
    result = user_collection.find(user_query)

    if any(u['user_email'] == user_email for u in result):
        result.rewind()
        user_dict = result.next()
        user = get_user_from_dict(user_dict)

        if user.sex is not None and user.weight and user.height_cm and user.age:
            recommendations, distances = get_meal_recommendation_list(user.sex, user.weight, user.height_cm, user.age,
                                                                      ActivityFactor.MEDIUM.value)
            return json.dumps({'success': True, 'recommendations': recommendations}), 200, {
                'ContentType': 'application/json'}
        else:
            return json.dumps({'success': False,
                               'error_message': 'Seems like your profile is incomplete, please fill out your profile data'}), 412, {
                       'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False, 'error_message': 'Could not find user'}), 404, {
            'ContentType': 'application/json'}


@app.route('/prediction/<string:weekday>/<string:time>/<string:alexa_api_access_token>', methods=['POST', 'GET'])
def date_time_prediction(weekday, time, alexa_api_access_token):
    gluco_doc_db = get_database()
    user_collection = gluco_doc_db['User']
    user_email = get_user_email(alexa_api_access_token)
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

        gluco_doc_db = get_database()
        user_collection = gluco_doc_db['User']
        cursor = user_collection.find({})

        for user_dict in cursor:

            user = get_user_from_dict(user_dict)

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
    gluco_doc_db = get_database()
    user_collection = gluco_doc_db['User']
    user_email = get_user_email(alexa_api_access_token)
    user_query = {"user_email": user_email}
    result = user_collection.find(user_query)
    meal_tsv = pd.read_csv('../classifiers/meals/filtered_dataset.tsv', sep='\t')
    meal_row = meal_tsv.loc[meal_tsv['id'] == int(meal_id)]

    print(meal_row)

    json_row = json.loads(meal_row.loc['meals'])
    names = ''

    for dish in json_row['dishes']:
        names += dish['name']

    if any(u['user_email'] == user_email for u in result):
        result.rewind()
        user_dict = result.next()
        user = get_user_from_dict(user_dict)
        date = datetime.datetime.now().date()
        send_email(user_email, "Your Meal Details (" + date + ")", names)

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return e, 400


def get_database():
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb+srv://glucoDoc:glucoDoc@glucodoc.f8dds.mongodb.net/GlucoDoc?retryWrites=true&w=majority"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    from pymongo import MongoClient
    client = MongoClient(CONNECTION_STRING, ssl_cert_reqs=ssl.CERT_NONE)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['GlucoDoc']


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
    app.run(debug=True, host='0.0.0.0', port=5002)
