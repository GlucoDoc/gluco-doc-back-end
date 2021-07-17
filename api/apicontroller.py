import os

import werkzeug
from dateutil.parser import *
from joblib import load
from datetime import date

from flask import Flask

# Loading model
from werkzeug.exceptions import BadRequest

print("Loading model from: {}".format('trained_model.joblib'))
inference_lda = load('trained_model.joblib')

# Creation of the Flask app
app = Flask(__name__)


# Flask route so that we can serve HTTP traffic on that route
@app.route('/prediction/<string:weekday>/<string:time>', methods=['POST', 'GET'])
def date_time_prediction(weekday, time):
    weekday_number = int(weekday)
    time_number = int(time)
    if weekday_number < 0 or weekday_number > 7:
        raise BadRequest('Weekday (' + weekday + ') out of range')
    if time_number < 0 or time_number > 24:
        raise BadRequest('Time (' + time + ') out of range')

    time = time[1] if len(time) > 1 else time

    classified_model = load('trained_model.joblib')
    result = classified_model.predict([[str(weekday), str(time)]])

    return {'prediction': result[0]}


@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return e, 400


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
