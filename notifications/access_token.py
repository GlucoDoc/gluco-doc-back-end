import json

import requests
from notifications.credentials import key
import logging

# Token access constants
CLIENT_ID = key['CLIENT_ID']
CLIENT_SECRET = key['CLIENT_SECRET']
UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.00Z"
TOKEN_URI = "https://api.amazon.com/auth/o2/token"
ALEXA_URI = "https://api.amazonalexa.com/v1/proactiveEvents/stages/development"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_access_token():
    token_params = {
        "grant_type": "client_credentials",
        "scope": "alexa::proactive_events",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    token_headers = {
        "Content-Type": "application/json;charset=UTF-8"
    }

    response = requests.post(TOKEN_URI, headers=token_headers, data=json.dumps(token_params), allow_redirects=True)

    logger.info("Token response status: " + format(response.status_code))
    logger.info("Token response body  : " + format(response.text))

    if response.status_code != 200:
        logger.info("Error calling LWA!")
        return None

    access_token = json.loads(response.text)["access_token"]
    return access_token
