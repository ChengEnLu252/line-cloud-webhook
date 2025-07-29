import psycopg2, requests, os
from line_bot.handlers import handle_text  # 直接復用你的解析 & 寫入
from linebot.v3.messaging import MessagingApi, ApiClient, Configuration
from linebot.v3.messaging.models import PushMessageRequest, TextMessage

cfg = Configuration(access_token=os.getenv("CHANNEL_ACCESS_TOKEN"))
DB  = os.getenv("REMOTE_DB")   # = Render DATABASE_URL

def push(uid, msg):
    with ApiClient(cfg) as api:
        MessagingApi(api).push_message(PushMessageRequest(to=uid, messages=[TextMessage(text=msg)]))

def main():
    conn = psycopg2.connect(DB)
    cur  = conn.cursor()
    cur.execute("SELECT id, user_id, raw FROM pending_records ORDER BY id")
    rows = cur.fetchall()
    for rid, uid, raw in rows:
        msg = handle_text(raw)          # 讓現有邏輯寫入本機 SQLite & 回覆字串
        push(uid, "感謝等待！" + msg.split("\n")[0] + "\n✅ 已補上紀錄")
        cur.execute("DELETE FROM pending_records WHERE id=%s", (rid,))
        conn.commit()

if __name__ == "__main__":
    main()
