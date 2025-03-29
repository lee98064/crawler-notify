import time
from services.kenshiyonezu import check_stock

PRODUCT_LIST = [
    {
        "name": "'JUNK ステッカー GO'",
        "url":  "https://shop.kenshiyonezu.jp/products/tp-rky-381"
    },
    {
        "name": "いきものショルダー",
        "url":  "https://shop.kenshiyonezu.jp/products/tp-rky-370"
    }
]

STATE_TABLE = {}


def message_to_template(new_status: str, product_name: str, product_url: str) -> dict:
    """
    將狀態轉換成 Telegram 卡片樣式的字典
    """
    # 你可以依照實際需求客製文字
    if new_status == 'in_stock':
        headline = f"🟢 有庫存：{product_name}\n"
        text_message = "現在可購買，點下方按鈕前往"
    else:
        headline = f"🔴 缺貨：{product_name}\n"
        text_message = "目前顯示無庫存或已售完"

    # Inline Keyboard 結構 (類似卡片 + 按鈕)
    # 參考官方文件: https://core.telegram.org/bots/api#inlinekeyboardmarkup
    keyboard = [
        [
            {
                "text": "前往商品頁面",  # 按鈕上顯示的文字
                "url":  product_url   # 按下後要連到哪裡
            }
        ]
    ]
    reply_markup = {
        "inline_keyboard": keyboard
    }

    return {
        "headline":     headline,
        "text_message": text_message,
        "reply_markup": reply_markup
    }
    

def main():
    while True:
        for product in PRODUCT_LIST:
            product_name = product["name"]
            product_url  = product["url"]

            current_status = check_stock(product_url)

            if current_status == "unknown":
                # 若要在 unknown 時發送通知，可自行決定
                print(f"商品「{product_name}」狀態未知(unknown)。")
                continue

            if product_url not in STATE_TABLE:
                # 第一次執行，初始化狀態
                STATE_TABLE[product_url] = current_status
                print(f"初始化狀態：{product_name} => {current_status}")
                # 可決定是否要在首次執行時就通知
                continue

            prev_status = STATE_TABLE[product_url]
            # 只有在狀態改變時才通知
            if current_status != prev_status:
                STATE_TABLE[product_url] = current_status
                print(f"【狀態改變】{product_name} 由「{prev_status}」→「{current_status}」")
                send_telegram_card(message_to_template(current_status, product_name, product_url))
            else:
                # 侯認為狀態沒變就不通知
                print(f"商品「{product_name}」狀態未變：{current_status}")

        time.sleep(10)  # 10分鐘 = 600秒

if __name__ == "__main__":
    main()