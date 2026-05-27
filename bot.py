import os
import requests
import time
import threading
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URL = "https://n170404.alteg.io/company/773361/personal/select-time?o=m3031495s10838308"


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


def check_page():
    r = requests.get(URL, timeout=30)
    return r.text


def bot_loop():
    print("Бот запущен")
    send_message("Бот запущен 🚀")

    old = ""

    while True:
        try:
            page = check_page()

            # если страница изменилась
            if old and page != old:
                send_message("🔥 Изменения в расписании!")
                print("Изменение!")

            old = page

        except Exception as e:
            print("Ошибка:", e)

        time.sleep(1200)  # 20 минут


# запускаем бот в фоне
threading.Thread(target=bot_loop, daemon=True).start()


# Flask нужен только чтобы Render не выключил сервис
@app.route("/")
def home():
    return "Bot is alive"


# запуск сервера (ВАЖНО для Render)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
