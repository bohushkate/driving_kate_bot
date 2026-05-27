import os
import requests
import time

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URL = "https://n170404.alteg.io/company/773361/personal/select-time?o=m3031495s10838308"

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def check_page():
    r = requests.get(URL)
    return r.text

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

    time.sleep(1200)
