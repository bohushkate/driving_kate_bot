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
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except Exception as e:
        print("Telegram error:", e)


# ---------------- PLAYWRIGHT ----------------
def get_page_html():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )

            page = browser.new_page()

            print("➡️ Opening page...")
            page.goto(URL, timeout=60000)

            time.sleep(8)

            html = page.content()

            print("📦 HTML SIZE:", len(html))

            browser.close()
            return html

    except Exception as e:
        print("❌ Playwright error:", e)
        return ""


# ---------------- PARSER ----------------
def extract_slots(html):
    import re
    slots = re.findall(r"\b([01]?\d|2[0-3]):[0-5]\d\b", html)
    return slots


# ---------------- BOT LOOP ----------------
def bot_loop():
    print("🚀 STARTING BOT LOOP")
    send_message("🚀 Бот запущен")

    last_slots = set()

    while True:
        try:
            print("\n🌀 LOOP TICK - checking site...")

            html = get_page_html()

            if not html:
                print("⚠️ Empty HTML received")
                time.sleep(60)
                continue

            print("🔎 Parsing HTML...")
            slots = set(extract_slots(html))

            print("📊 FOUND:", slots)

            new_slots = slots - last_slots

            if new_slots:
                msg = "🔥 Новые слоты:\n" + "\n".join(sorted(new_slots))
                send_message(msg)
                print("📤 Sent:", new_slots)
            else:
                print("😴 No new slots")

            last_slots = slots

        except Exception as e:
            print("💥 LOOP ERROR:", e)
            send_message(f"Ошибка: {e}")

        time.sleep(60)


# ---------------- FLASK ----------------
@app.route("/")
def home():
    return "Bot is alive"


# ---------------- START ----------------
def start_bot():
    time.sleep(3)
    bot_loop()


if __name__ == "__main__":
    print("🚀 STARTING APP")

    t = threading.Thread(target=start_bot, daemon=True)
    t.start()

    app.run(host="0.0.0.0", port=10000)
