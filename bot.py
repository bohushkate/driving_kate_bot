import os
import time
import threading
import requests
import re

from flask import Flask
from playwright.sync_api import sync_playwright

app = Flask(__name__)

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# ----- URL = "https://n170404.alteg.io/company/773361/personal/select-time?o=m3031495s10838308"
URL = "https://n170404.alteg.io/company/773361/personal/select-time?o=m2824298s10838308"


# ---------------- TELEGRAM ----------------
def send_message(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text}
        )
    except Exception as e:
        print("Telegram error:", e)


# ---------------- PLAYWRIGHT ----------------
def get_page_html():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )

        page = browser.new_page()

        print("➡️ OPENING URL:", URL)

        response = page.goto(URL, timeout=60000)

        print("➡️ HTTP STATUS:", response.status if response else "NO RESPONSE")

        # даём JS догрузиться
        page.wait_for_timeout(8000)

        html = page.content()

        print("➡️ HTML SIZE:", len(html))
        print("➡️ HTML PREVIEW:\n", html[:800])

        browser.close()
        return html


# ---------------- PARSE ----------------
def extract_slots(html):
    return re.findall(r"\b([01]?\d|2[0-3]):[0-5]\d\b", html)


# ---------------- BOT LOOP ----------------
def bot_loop():
    print("Бот запущен")
    send_message("Бот запущен 🚀")

    last_slots = set()

    while True:
        try:
            print("🔄 Checking site...")

            html = get_page_html()

            # ❗ защита от пустой страницы
            if not html or len(html) < 1000:
                print("❌ EMPTY HTML DETECTED")
                send_message("⚠️ Пустой HTML (страница не загрузилась или блокировка)")
                time.sleep(60)
                continue

            slots = set(extract_slots(html))

            print("🎯 SLOTS FOUND:", slots)

            new_slots = slots - last_slots

            if new_slots:
                msg = "🔥 Новые слоты:\n" + "\n".join(sorted(new_slots))
                send_message(msg)
                print("📩 SENT:", new_slots)

            last_slots = slots

        except Exception as e:
            print("❌ ERROR:", e)
            send_message(f"Ошибка: {e}")

        time.sleep(60)


# ---------------- FLASK ----------------
@app.route("/")
def home():
    return "Bot is alive"


# ---------------- START ----------------
def start_bot():
    thread = threading.Thread(target=bot_loop, daemon=True)
    thread.start()


start_bot()

if __name__ == "__main__":
    print("Flask starting...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
