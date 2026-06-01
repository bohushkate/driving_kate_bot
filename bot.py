import os
import time
import threading
import requests
from flask import Flask
from playwright.sync_api import sync_playwright

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# ----- URL = "https://n170404.alteg.io/company/773361/personal/select-time?o=m3031495s10838308"
URL = "https://n170404.alteg.io/company/773361/personal/select-time?o=m2824298s10838308"


# ---------------- TELEGRAM ----------------
def send_message(text):
    if not TOKEN or not CHAT_ID:
        print("Telegram env vars missing")
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
            timeout=10
        )
    except Exception as e:
        print("Telegram error:", e)


# ---------------- PLAYWRIGHT ----------------
def get_page_html():
    print("▶ запускаю playwright")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )

        page = browser.new_page()
        page.goto(URL, timeout=60000)

        time.sleep(5)

        html = page.content()

        browser.close()

        print("✔ html получен, длина:", len(html))
        return html


# ---------------- PARSE ----------------
def extract_slots(html):
    import re
    return re.findall(r"\b([01]?\d|2[0-3]):[0-5]\d\b", html)


# ---------------- BOT LOOP ----------------
def bot_loop():
    print("🔥 BOT LOOP STARTED")
    send_message("Бот запущен 🚀")

    last_slots = set()

    while True:
        try:
            print("🔎 Проверяю сайт...")

            html = get_page_html()

            if not html:
                print("⚠ HTML EMPTY")
                send_message("HTML пустой")
                continue

            slots = set(extract_slots(html))

            print("📦 slots:", slots)

            new_slots = slots - last_slots

            if new_slots:
                msg = "🔥 Новые слоты:\n" + "\n".join(sorted(new_slots))
                send_message(msg)

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
if __name__ == "__main__":
    print("🚀 STARTING APP")

    t = threading.Thread(target=bot_loop)  # ❗ без daemon
    t.start()

    app.run(host="0.0.0.0", port=10000)
