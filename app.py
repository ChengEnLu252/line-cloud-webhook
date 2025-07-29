from flask import Flask, request
from linebot.v3 import WebhookParser
from linebot.v3.webhooks import MessageEvent, TextMessageContent, FollowEvent
from linebot.v3.messaging import MessagingApi, ApiClient, Configuration
from linebot.v3.messaging.models import ReplyMessageRequest, TextMessage
import os, psycopg2

app = Flask(__name__)
parser = WebhookParser(os.getenv("CHANNEL_SECRET"))
cfg   = Configuration(access_token=os.getenv("CHANNEL_ACCESS_TOKEN"))

def _reply(token, text):
    with ApiClient(cfg) as api:
        MessagingApi(api).reply_message(
            ReplyMessageRequest(reply_token=token, messages=[TextMessage(text=text)])
        )

def _save_to_db(user_id, raw):
    sql = "INSERT INTO pending_records(user_id, raw) VALUES(%s,%s)"
    with psycopg2.connect(os.getenv("DATABASE_URL")) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id, raw))

@app.route("/callback", methods=["POST"])
def callback():
    events = parser.parse(request.get_data(as_text=True),
                          request.headers.get("X-Line-Signature",""))
    for ev in events:
        if isinstance(ev, FollowEvent):
            _reply(ev.reply_token, "Hi！我是健康紀錄小助手，目前後台休息中，之後會補記錄喔😊")
        elif isinstance(ev, MessageEvent) and isinstance(ev.message, TextMessageContent):
            _save_to_db(ev.source.user_id, ev.message.text)
            _reply(ev.reply_token, "此程式目前休息中 ✅ 已暫存您的輸入，稍後會補記錄！")
    return "OK"
