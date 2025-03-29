from utils.env import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_API_URL
from utils.requests import BaseUrlSession
import json

telegram_request = BaseUrlSession(TELEGRAM_API_URL)

def send_msg(msg:str):
    assert type(msg) == str, "傳入訊息必須為字串"
    url = f'/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={msg}'
    r = telegram_request.get(url)
    
    return r.status_code == 200



def send_telegram_card(chat_params: dict):
    """
    以類似卡片的方式，傳送包含按鈕、粗體文字到 Telegram。
      - new_status: 'in_stock' or 'out_of_stock'
    """
    # 利用 Telegram sendMessage API
    url = f"/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       f"{chat_params['headline']}{chat_params['text_message']}",
        "parse_mode": "Markdown",  # 也可用 "HTML"
        "reply_markup": json.dumps(chat_params['reply_markup'])
    }
    resp = telegram_request.post(url, data=payload, timeout=10)
    if resp.status_code == 200:
        print("[Telegram] 已發送卡片樣式通知")
    else:
        print("[Telegram] 傳送失敗，狀態碼:", resp.status_code, resp.text)