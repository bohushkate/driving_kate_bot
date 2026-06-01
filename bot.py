import os
import time
import threading
import requests
from flask import Flask
from playwright.sync_api import sync_playwright

app = Flask(__name__)

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URL = "https://n170404.alteg.io/company/773361/personal/select-time?o=m3031495s10838308"


# ---------------- TELEGRAM ----------------
def send_message(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except Exception as e:
        print("Telegram error:", e)


# ---------------- PLAYWRIGHT ----------------
def get_page_html():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, timeout=60000)
        time.sleep(5)  # дать JS прогрузиться

        html = page.content()

        browser.close()
        return html


# ---------------- ПАРСИНГ ----------------
def extract_slots(html):
    # максимально простой способ (чтобы не ломалось)
    # ищем любые времена типа 08:00 - 19:00
    import re
    return re.findall(r"\b([01]?\d|2[0-3]):[0-5]\d\b", html)


# ---------------- ОСНОВНОЙ ЦИКЛ ----------------
def bot_loop():
    print("Бот запущен")
    send_message("Бот запущен 🚀")

    last_slots = set()

    while True:
        try:
            print("Проверяю сайт...")

            html = get_page_html()
            slots = set(extract_slots(html))

            print("Найдено:", slots)

            new_slots = slots - last_slots

            if new_slots:
                msg = "🔥 Найдены слоты:\n" + "\n".join(sorted(new_slots))
                send_message(msg)
                print("Отправлено:", new_slots)

            last_slots = slots

        except Exception as e:
            print("Ошибка:", e)
            send_message(f"Ошибка: {e}")

        time.sleep(60)


# ---------------- FLASK ----------------
@app.route("/")
def home():
    return "Bot is alive"


# ---------------- START ----------------
if __name__ == "__main__":
    thread = threading.Thread(target=bot_loop)
    thread.start()

    app.run(host="0.0.0.0", port=10000)
