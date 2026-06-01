import os
import time
import threading
import requests
from flask import Flask
from playwright.sync_api import sync_playwright

app = Flask(__name__)

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# ----- URL = "https://n170404.alteg.io/company/773361/personal/select-time?o=m3031495s10838308"
URL = "https://n170404.alteg.io/company/773361/personal/select-time?o=m2824298s10838308"


def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text},
        timeout=20
    )


def get_bold_days():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, timeout=60000)
        page.wait_for_timeout(5000)

        # ⚠️ ВАЖНО: тут мы ищем кликабельные дни календаря
        # в таких системах они обычно button/div с классами типа "active", "available", "bold"
        elements = page.query_selector_all(
            "td:not(.disabled), .day:not(.disabled), .calendar-day:not(.disabled)"
        )

        result = []

        for el in elements:
            text = el.inner_text().strip()

            # фильтр: только числа (дни месяца)
            if text.isdigit():
                # проверяем что элемент кликабельный / активный
                classes = el.get_attribute("class") or ""

                if any(x in classes.lower() for x in ["active", "bold", "available", "free"]):
                    result.append(text)

        browser.close()
        return result


def bot_loop():
    print("bot started")
    send_message("Бот запущен 🚀")

    last = set()

    while True:
        try:
            days = set(get_bold_days())
            print("available days:", days)

            if days and days != last:
                send_message(f"🔥 Доступные дни: {', '.join(sorted(days))}")

            last = days

        except Exception as e:
            print("error:", e)

        time.sleep(600)


threading.Thread(target=bot_loop, daemon=True).start()


@app.route("/")
def home():
    return "alive"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
