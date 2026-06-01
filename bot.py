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
        time.sleep(5)

        html = page.content()

        browser.close()
        return html


# ---------------- PARSE ----------------
def extract_slots(html):
    import re
    return re.findall(r"\b([01]?\d|2[0-3]):[0-5]\d\b", html)


# ---------------- BOT LOOP ----------------
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
                msg = "🔥 Новые слоты:\n" + "\n".join(sorted(new_slots))
                send_message(msg)
                print("Отправлено:", new_slots)

            last_slots = slots

        except Exception as e:
            print("Ошибка:", e)
            send_message(f"Ошибка: {e}")

        time.sleep(60)


# ---------------- FLASK ROUTE ----------------
@app.route("/")
def home():
    return "Bot is alive"


# ---------------- START ----------------
def start_bot():
    time.sleep(3)  # даём Flask подняться
    bot_loop()


if __name__ == "__main__":
    threading.Thread(target=start_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
