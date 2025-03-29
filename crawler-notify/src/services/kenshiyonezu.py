import requests
from bs4 import BeautifulSoup

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

def check_stock(url: str) -> str:
    """
    檢查商品是否有庫存。
      - 回傳 'in_stock' 或 'out_of_stock'。
      - 依據 HTML 結構判斷：若購物車按鈕是可點擊 => in_stock；若 disabled 或顯示 '在庫確認中' => out_of_stock
    """
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"[ERROR] 無法連線 {url}, 錯誤: {e}")
        return "unknown"

    soup = BeautifulSoup(resp.text, "html.parser")
    # 查找加入購物車按鈕
    add_btn = soup.find("button", {"type": "submit", "name": "add", "class": "product-form__submit"})

    if not add_btn:
        # 沒找到按鈕代表未知狀態 (頁面模板變動或商品被移除)
        return "unknown"

    # 如果按鈕有 disabled 屬性、或文字包含"在庫確認中"、"SOLD OUT" 等 => 缺貨
    if add_btn.has_attr("disabled"):
        return "out_of_stock"
    
    btn_text = add_btn.get_text(strip=True) or ""
    if "在庫確認中" in btn_text or "SOLD OUT" in btn_text.upper():
        return "out_of_stock"

    # 否則視為有貨
    return "in_stock"