import json

import google.auth.transport.requests
import requests
from google.oauth2 import service_account
from loguru import logger

PROJECT_ID = 'epaction-7c149'
BASE_URL = 'https://fcm.googleapis.com'
FCM_ENDPOINT = 'v1/projects/' + PROJECT_ID + '/messages:send'
FCM_URL = BASE_URL + '/' + FCM_ENDPOINT
SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
FIREBASE_CONFIG = 'conf2.json'


def _get_access_token():
    credentials = service_account.Credentials.from_service_account_file(FIREBASE_CONFIG, scopes=SCOPES)
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token


def send_fcm_message():
    message = {
        'message': {
            "token": "",
            'notification': {
                'title': 'EPaction',
                'body': 'Необходимо пройти проверку'
            }

        }
    }
    headers = {
        'Authorization': 'Bearer ' + _get_access_token(),
        'Content-Type': 'application/json; UTF-8',
    }
    resp = requests.post(FCM_URL, data=json.dumps(message), headers=headers)

    if resp.status_code == 200:
        logger.info('Message sent to Firebase for delivery, response:')
    else:
        logger.exception(f'Unable to send message to Firebase: {resp.text}')
