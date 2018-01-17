from __future__ import print_function
import json
from datetime import datetime
import pytz

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
    SERVICE_ACCOUNT_FILE,
    # APPLICATION_NAME,
    SPREADSHEET_ID,
    SHEET_TAB,
    # LINE_CHANNEL_ID,
    # LINE_CHANNEL_SECRET,
    LINE_CALLBACK_URI,
    LINE_CHANNEL_ACCESS_TOKEN,
    TIME_ZONE_COUNTRY
)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

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

def write(*args):
    """Write the billinge to Spread sheet
    """
    service = discovery.build('sheets', 'v4', 
            credentials=get_credentials(),
            discoveryServiceUrl=('https://sheets.googleapis.com/$discovery/rest?version=v4'))

    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID, range=f"{SHEET_TAB}!A2:C3",
        valueInputOption="RAW",
        body=dict(values=[
            [
                datetime.now(pytz.timezone(pytz.country_timezones(TIME_ZONE_COUNTRY)[0])).strftime("%Y-%m-%d %H:%M:%S"), 
                args[0], 
                int(args[1]), 
                ' '.join(args[2:])if len(args) > 2 else ""
            ]
        ])).execute()
    print('{0} cells updated.'.format(result['updates'].get('updatedCells')))


@app.route(LINE_CALLBACK_URI, methods=['POST'])
def callback():
    # TODO: validate by Signature
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    # handle webhook body
    try:
        for e in json.loads(body)['events']:
            write(*(e['message']['text'].split()))

            line_bot_api.reply_message(e['replyToken'],
            TextSendMessage(text="OK"))


    except InvalidSignatureError as e:
        print(e)
        abort(400)


    return 'OK'


if __name__ == "__main__":
    app.run()


