from __future__ import print_function

from google.oauth2 import service_account
from apiclient import discovery
from oauth2client import tools
from flask import Flask, request, abort


from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

from config import (
    SCOPES,
    SERVICE_ACCOUNT_FILE,
    APPLICATION_NAME,
    SPREADSHEET_ID,
    SHEET_TAB,
    LINE_CHANNEL_ID,
    LINE_CHANNEL_SECRET
)

app = Flask(__name__)


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

line_bot_api = LineBotApi(LINE_CHANNEL_SECRET)
handler = WebhookHandler(LINE_CHANNEL_ID)


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



@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    write()
    # app.run()


