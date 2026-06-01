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

URL = "https://n170404.alteg.io/company/773361/personal/select-time?o=m3031495s10838308"


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except Exception as e:
        print("Ошибка отправки:", e)


def extract_times(html):
    # ищем все времена формата 08:00–19:59
    times = re.findall(r'\b([0-1]\d|2[0-3]):[0-5]\d\b', html)

    # фильтр только 08:00–19:00
    filtered = []
    for t in times:
        h = int(t.split(":")[0])
        if 8 <= h <= 19:
            filtered.append(t)

    return sorted(set(filtered))


def check_slots():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()

        page.goto(URL, timeout=60000)
        page.wait_for_timeout(7000)

        content = page.content()
        browser.close()
        return content


def bot_loop():
    print("Бот запущен")
    send_message("Бот запущен 🚀")

    last_times = set()

    while True:
        try:
            html = check_slots()
            times = set(extract_times(html))

            print("Найдено:", times)

            # новые слоты
            new_times = times - last_times

            if new_times:
                msg = "🔥 Новые слоты:\n" + "\n".join(sorted(new_times))
                send_message(msg)
                print("Отправил:", new_times)

            last_times = times

        except Exception as e:
            print("Ошибка:", e)

        time.sleep(60)  # проверка каждую минуту


threading.Thread(target=bot_loop, daemon=True).start()


@app.route("/")
def home():
    return "Bot is alive"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
