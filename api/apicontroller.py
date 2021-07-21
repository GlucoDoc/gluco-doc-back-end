import datetime
import os

from joblib import load

from datetime import datetime, timedelta

from flask import Flask
from flask import request
import http.client
# Loading model
from werkzeug.exceptions import BadRequest
from classifier.data_processor import process_data
from classifier.classifier import train_model
import pickle
import threading

# print("Loading model from: {}".format('trained_model.joblib'))
# inference_lda = load('trained_model.joblib')

# Creation of the Flask app
app = Flask(__name__)

TRAINING_MODEL = False


@app.route('/')
def default():
    return "<html><head><style>h1 {text-align: center;}p {text-align: center;}div {text-align: center;}body " \
           "{background-color: #32a852;}body {color: white;}</style></head><body><h1>Gluco - Doc API</h1></body></html>"


@app.route('/VerifyModelIntegrity/<string:access_token>/')
def verify_model_integrity(access_token):

    def train_model_thread():

        print('hellooo im the thread!')

        last_model_date = datetime.now()

        if os.path.exists('last_model_date.pickle'):
            last_model_date = pickle.load(open('last_model_date.pickle', 'rb'))

        if (not os.path.exists('last_model_date.pickle')) or (not os.path.exists('trained_model.joblib')) or\
                ((datetime.now() - last_model_date) >= timedelta(1)):

            global TRAINING_MODEL

            TRAINING_MODEL = True

            conn = http.client.HTTPSConnection("sandbox-api.dexcom.com")

            headers = {
                'authorization': "Bearer " + access_token
            }

            start_date = (datetime.now() - timedelta(91)).isoformat()
            end_date = (datetime.now() - timedelta(1)).isoformat()

            conn.request("GET", "/v2/users/self/egvs?startDate=" + start_date + "&endDate=" + end_date, headers=headers)

            res = conn.getresponse()
            json_data_string = res.read().decode("utf-8")

            pickle.dump(datetime.now(), open('last_model_date.pickle', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
            process_data(json_data_string)
            train_model()

            TRAINING_MODEL = False

    th = threading.Thread(target=train_model_thread)
    th.start()

    return 'success'


@app.route('/Prediction/<string:weekday>/<string:time>', methods=['POST', 'GET'])
def date_time_prediction(weekday, time):

    if not os.path.exists('trained_model.joblib'):
        return {
            'prediction': None,
            'training_model': True
        }

    weekday_number = int(weekday)
    time_number = int(time)
    if weekday_number < 0 or weekday_number > 7:
        raise BadRequest('Weekday (' + weekday + ') out of range')
    if time_number < 0 or time_number > 24:
        raise BadRequest('Time (' + time + ') out of range')

    time = time[1] if len(time) > 1 else time

    classified_model = load('trained_model.joblib')
    result = classified_model.predict([[str(weekday), str(time)]])

    return {
        'prediction': result[0],
        'training_model': False
    }


@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return e, 400


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
