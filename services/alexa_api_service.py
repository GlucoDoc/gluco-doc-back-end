import requests

ALEXA_URI = 'https://api.amazonalexa.com/v2/'

def get_user_email(access_token):

    headers = {
        "Authorization": "Bearer {}".format(access_token),
        "Content-Type": "application/json"
    }

    response = requests.get(ALEXA_URI + 'accounts/~current/settings/Profile.email', headers=headers, allow_redirects=True)

    return str(response.json())


def get_user_timezone(access_token, device_id):

    headers = {
        "Authorization": "Bearer {}".format(access_token),
        "Content-Type": "application/json"
    }

    response = requests.get(ALEXA_URI + 'devices/{deviceId}/settings/System.timeZone'.format(deviceId=device_id), headers=headers, allow_redirects=True)

    return str(response.json())

