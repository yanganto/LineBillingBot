from __future__ import print_function
import json

from google.oauth2 import service_account
from apiclient import discovery
from oauth2client import tools
from flask import Flask, request, abort


from linebot import (
    LineBotApi
    # WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    # MessageEvent, 
    # TextMessage, 
    TextSendMessage
)

from config import (
    SCOPES,
    SERVICE_ACCOUNT_FILE,
    # APPLICATION_NAME,
    SPREADSHEET_ID,
    SHEET_TAB,
    # LINE_CHANNEL_ID,
    # LINE_CHANNEL_SECRET,
    LINE_CALLBACK_URI,
    LINE_CHANNEL_ACCESS_TOKEN
)

app = Flask(__name__)


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
#handler = WebhookHandler(LINE_CHANNEL_ID)


def get_credentials():
    """Gets valid credentials 
        Credentials, the obtained credential.
    """

    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return credentials

def write():
    """Write the billinge to Spread sheet
    """
    service = discovery.build('sheets', 'v4', 
            credentials=get_credentials(),
            discoveryServiceUrl=('https://sheets.googleapis.com/$discovery/rest?version=v4'))

    rangeName = f"{SHEET_TAB}!A1:10"
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s' % (row[0]))

@app.route(LINE_CALLBACK_URI, methods=['POST'])
def callback():
    # TODO: validate by Signature
    # get X-Line-Signature header value
    # signature = request.headers.get('X-Line-Signature')

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        line_bot_api.reply_message(json.loads(body)['events'][0]['replyToken'],
        TextSendMessage(text='I got it!'))
    except InvalidSignatureError as e:
        print(e)
        abort(400)


    return 'OK'


if __name__ == "__main__":
    app.run()


