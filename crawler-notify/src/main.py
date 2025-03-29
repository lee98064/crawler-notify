#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask + SQLite + Telegram 範例，HTML、JS 分檔：
   - monitor.py : Python後端 (Flask server)
   - templates/index.html : 前端 HTML
   - static/js/index.js   : 前端 JavaScript
"""
import os
import time
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from services.kenshiyonezu import check_stock, message_to_template
from utils.telegram import send_telegram_card
from flask import Flask, request, redirect, url_for, render_template
from utils.env import JOB_EXECUTION_INTERVAL

# --------------------- 基本設定 ---------------------
path = os.path.dirname(os.path.realpath(__file__))
DB_NAME = "../db/monitor.db"

scheduler = BackgroundScheduler()

app = Flask(__name__)

# --------------------- 資料庫: 建立資料表 ---------------------
def init_db():
    """
    建立 watch_list 資料表，假如不存在的話。
    """
    with sqlite3.connect(os.path.join(path, DB_NAME)) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS watch_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            last_state TEXT DEFAULT 'unknown',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()

def get_db_connection():
    """取得 SQLite 連線"""
    return sqlite3.connect(os.path.join(path, DB_NAME))

def run_check_all():
    """ 針對 watch_list 裡的商品依序檢查，狀態改變則發送 Telegram 通知 """
    print(f"[Info] 開始檢查庫存狀態... {time.strftime('%Y-%m-%d %H:%M:%S')}")
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, url, last_state FROM watch_list")
    rows = c.fetchall()

    for row in rows:
        item_id = row[0]
        product_name = row[1]
        product_url  = row[2]
        last_state   = row[3]
        
        # 檢查庫存狀態
        new_state = check_stock(product_url)
        print(f"[Info] 檢查商品: {product_name}, 狀態: {new_state}")
        if new_state != last_state and new_state != "unknown":
            print(f"[Info] 狀態改變: {product_name} {last_state} -> {new_state}")
            send_telegram_card(message_to_template(new_state, product_name, product_url))

        # 不論是否相同，都更新DB(unknown=>unknown也OK)
        if new_state != last_state:
            sql = """
                UPDATE watch_list
                   SET last_state = ?,
                       updated_at = CURRENT_TIMESTAMP
                 WHERE id = ?
            """
            c.execute(sql, (new_state, item_id))
            conn.commit()
        print(f"[Info] 更新狀態: {product_name} {last_state} -> {new_state}")
    print("[Info] 檢查完成。")
    print("=" * 40)
    conn.close()

# --------------------- Flask 路由 ---------------------
@app.route("/")
def index():
    """顯示監控清單畫面 (對應 templates/index.html)"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, url, last_state FROM watch_list ORDER BY id")
    rows = c.fetchall()
    conn.close()

    # render_template() 會去 templates/ 找 index.html
    return render_template("index.html", rows=rows)

@app.route("/add", methods=["POST"])
def add_item():
    """建立新的監控商品"""
    product_name = request.form.get("name","").strip()
    product_url  = request.form.get("url","").strip()

    if not product_name or not product_url:
        return "名稱或網址不可為空", 400

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO watch_list (name, url, last_state)
        VALUES (?, ?, 'unknown')
    """, (product_name, product_url))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/delete/<int:item_id>")
def delete_item(item_id):
    """刪除指定商品"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM watch_list WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/trigger_check")
def trigger_check():
    """手動觸發一次庫存檢查"""
    run_check_all()
    return "已執行檢查，請回上一頁或刷新。"

# --------------------- Main ---------------------
if __name__ == "__main__":
    init_db()
    
    scheduler.add_job(run_check_all, trigger='interval', seconds=JOB_EXECUTION_INTERVAL)
    scheduler.start()
    # 建議用 Thread 或 crontab 週期呼叫 /trigger_check
    app.run(host="0.0.0.0", port=5000, debug=False)