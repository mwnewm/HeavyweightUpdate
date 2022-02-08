from twilio.rest import Client
import dependencies
import logging
import requests
from datetime import datetime

# base URL of all Spotify API endpoints
BASE_URL = 'https://api.spotify.com/v1/'
AUTH_URL = 'https://accounts.spotify.com/api/token'
HEAVYWEIGHT_ID = '5c26B28vZMN8PG0Nppmn5G'
DISTRO_LIST = [
    dependencies.NUM1
]
SPOTIFY_CLIENT_ID = dependencies.SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = dependencies.SPOTIFY_CLIENT_SECRET
TWILIO_ACCOUNT_SID = dependencies.TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = dependencies.TWILIO_AUTH_TOKEN
TWILIO_MESSAGE_SERVICE_SID = dependencies.TWILIO_MESSAGE_SERVICE_SID


def run():
    logging.basicConfig(filename='HWU_log', level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info('Starting Heavyweight Update processor')
    token = authorize_client()
    headers = {
        'Authorization': 'Bearer {token}'.format(token=token)
    }
    # check for new episodes
    days_since_last_heavyweight = check_release_date(headers)
    # if's been a week interval, send message
    if days_since_last_heavyweight == 0:
        logging.info('Sending new episode texts to distro list...')
        send_update_message()
    elif days_since_last_heavyweight%21 == 0:
        logging.info('It\'s been 3 weeks. Sending still waiting update texts to distro list...')
        send_update_message(days_since_last_heavyweight)
    else:
        logging.info('No need to send text.')
    logging.info('Closing processor')


def authorize_client():
    client_id = SPOTIFY_CLIENT_ID
    client_secret = SPOTIFY_CLIENT_SECRET

    # POST
    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })

    # convert the response to JSON
    auth_response_data = auth_response.json()

    # save the access token
    access_token = auth_response_data['access_token']
    logging.info('Successfully retrieved spotify token')
    return access_token


def check_release_date(headers):
    episode_response = requests.get(BASE_URL + 'shows/' + HEAVYWEIGHT_ID + '/episodes', headers=headers, params={
        'market': 'US',
        'limit': 1
    })
    episode_data = episode_response.json()['items'][0]
    release_date_obj = datetime.strptime(episode_data['release_date'], '%Y-%m-%d').date()
    logging.info('Retrieved date of last Heavyweight episode: %s', release_date_obj.strftime('%d/%m/%Y'))
    today = datetime.now().date()
    return abs((today - release_date_obj).days)


# Send text
def send_update_message(days=0):
    account_sid = TWILIO_ACCOUNT_SID
    auth_token = TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    client.http_client.logger.setLevel(logging.INFO)

    if days > 0:
        message_body = "🎙 \n\n🎧 The Heavyweight Update 🎧\n\nIt's been " + str(days//7) \
                       + " weeks since the last Heavyweight! What gives!"
    else:
        message_body = \
            "🎙 \n\n🎧 The Heavyweight Update 🎧\n\nGood news, there is a new episode of Heavyweight on Spotify!"

    for number in DISTRO_LIST:
        message = client.messages.create(
            messaging_service_sid=TWILIO_MESSAGE_SERVICE_SID,
            body=message_body,
            to=number
        )

# run program
run()
