import time
import uuid
import json
import requests
import logging

from services.access_token_service import get_access_token


UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.00Z"
ALEXA_URI = "https://api.amazonalexa.com/v1/proactiveEvents/stages/development"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def send_notification(user_id):
    token = get_access_token()

    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json;charset=UTF-8"
    }

    logger.info("Headers: " + headers["Authorization"])

    seconds = time.time()
    timestamp = time.strftime(UTC_FORMAT, time.gmtime(seconds))
    reference_id = str(uuid.uuid4())
    seconds += 3600  # 1 hour for demo
    expiry_time = time.strftime(UTC_FORMAT, time.gmtime(seconds))

    logger.info("Timestamp: " + timestamp)
    logger.info("Expiry Time: " + expiry_time)
    logger.info("Reference ID: " + reference_id)

    params = {
        "timestamp": timestamp,
        "referenceId": reference_id,
        "expiryTime": expiry_time,

        "event": {
            "name": "AMAZON.MessageAlert.Activated",
            "payload": {
                "state": {
                    "status": "UNREAD",
                    "freshness": "NEW"
                },
                "messageGroup": {
                    "creator": {
                        "name": "GlucoDoc"
                    },
                    "count": 1
                }
            }
        },
        "relevantAudience": {
            "type": "Unicast",
            "payload": {
                "user": user_id
            }
        }
    }

    logger.info("Params Timestamp: " + params["timestamp"])
    logger.info("Params Expiry Time: " + params["expiryTime"])
    logger.info("Params Reference ID: " + params["referenceId"])

    res = requests.post(ALEXA_URI, headers=headers, data=json.dumps(params), allow_redirects=True)
    logger.info("done")
