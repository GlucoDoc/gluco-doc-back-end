import datetime
import os
import http.client
import pickle
import ssl
import threading
import json

from datetime import datetime, timedelta
from flask import Flask
from werkzeug.exceptions import BadRequest

from classifier.data_processor import process_data
from classifier.classifier import train_model
from notifications.notification import send_notification
from notifications.email_util import get_user_email, send_email_alert
from models.user import User

# Creation of the Flask app
app = Flask(__name__)

os.environ['DEXCOM_URI'] = "sandbox-api.dexcom.com"
os.environ['GLUCODOC_EMAIL_PASSWORD'] = "glucodoc2016"

os.environ['HYPERGLYCEMIA_THRESHOLD'] = "180"
os.environ['HYPOGLYCEMIA_THRESHOLD'] = "70"


@app.route('/')
def default():
    html_file = open("default_api_page.html", "r")
    return html_file.read()


@app.route('/updateUser/<string:access_token>/<string:user_id>/<string:alexa_user_access_token>')
def update_user(access_token, user_id, alexa_user_access_token):
    gluco_doc_db = get_database()
    user_collection = gluco_doc_db['User']

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
            user_query = {"user_id": user.user_id}
            user_update = {"$set": user.__dict__}
            user_collection.update_one(user_query, user_update)

    def train_model_thread():

        user_email = get_user_email(alexa_user_access_token)
        user = User(user_id, None, None, user_email)

        user_query = {"user_id": user_id}

        result = user_collection.find(user_query)

        if any(u['user_id'] == user_id for u in result):
            result.rewind()
            user_dict = result.next()

            if datetime.now() - user_dict['last_model_date'] >= timedelta(1):
                train_m(user, False)
        else:
            train_m(user, True)

    th = threading.Thread(target=train_model_thread)
    th.start()

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/prediction/<string:weekday>/<string:time>/<string:user_id>', methods=['POST', 'GET'])
def date_time_prediction(weekday, time, user_id):
    gluco_doc_db = get_database()
    user_collection = gluco_doc_db['User']

    user_query = {"user_id": user_id}
    result = user_collection.find(user_query)

    if any(u['user_id'] == user_id for u in result):
        result.rewind()
        user_dict = result.next()
        user = User(user_dict['user_id'], user_dict['model'], user_dict['last_model_date'], user_dict['user_email'])

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


@app.route('/notifications/<string:state>', methods=['POST', 'GET'])
def send_notifications_params(state):
    send_notifications(state)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/notifications', methods=['POST', 'GET'])
def send_notifications(state=None):
    def notification_thread():

        gluco_doc_db = get_database()
        user_collection = gluco_doc_db['User']

        for user_dict in user_collection:

            user = User(user_dict['user_id'], user_dict['model'], user_dict['last_model_date'], user_dict['user_email'])

            classified_model = pickle.loads(user.model)
            result = None

            if state is not None:
                result = [str(state)]
            else:
                result = classified_model.predict([[str(datetime.now().weekday()), str(datetime.now().hour)]])

            print(result)

            if result[0] == "hypoglycemia" or result[0] == "hyperglycemia":
                send_email_alert(user.user_email, result[0])
                send_notification(user.user_id)

    th = threading.Thread(target=notification_thread)
    th.start()

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return e, 400


def get_database():
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb+srv://glucoDoc:mUmg9B3PTcJuE988@glucodoc.f8dds.mongodb.net/GlucoDoc?retryWrites=true&w=majority"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    from pymongo import MongoClient
    client = MongoClient(CONNECTION_STRING, ssl_cert_reqs=ssl.CERT_NONE)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['GlucoDoc']


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
