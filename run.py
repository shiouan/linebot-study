import json
import os
import re
import configparser

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    QuickReply, QuickReplyButton, MessageAction)

from app.stock_helpers import get_stock
from app.fc_helpers import FcConsultant


config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), '.config', 'config.ini'))
# Channel Access Token
line_bot_api = LineBotApi(config['linebot']['channel_access_token'])
# Channel Secret
handler = WebhookHandler(config['linebot']['channel_secret'])

app = Flask(__name__)

fc_consultant = FcConsultant()

@app.route('/')
def index():
    return 'Hello world!'


@app.route('/test')
def test():
    return json.dump({2884:'玉山'})


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    quick_reply = None
    
    if re.findall('^@股票', event.message.text):
        message = '股市顧問進修中...\n'
    elif re.findall('^@利率', event.message.text):
        message, quick_reply= fc_consultant.anwser(event.message.text)
    else:
        message = event.message.text
    
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message, quick_reply=quick_reply))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
