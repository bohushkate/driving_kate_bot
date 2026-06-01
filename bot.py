import os
import time
import threading
import requests
from playwright.sync_api import sync_playwright

# ===== ENV =====
TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# ----- URL = "https://n170404.alteg.io/company/773361/personal/select-time?o=m3031495s10838308"
URL = "https://n170404.alteg.io/company/773361/personal/select-time?o=m2824298s10838308"

CHECK_EVERY = 60  # секунд

# ===== TELEGRAM =====
def send_message(text):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
            timeout=10
        )
        print("Telegram:", r.status_code)
    except Exception as e:
        print("Telegram error:", e)


# ===== CORE CHECK =====
def check_slots():
    found_slots = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("🌐 opening calendar...")
        page.goto(URL, timeout=60000)

        # ждём JS календарь
        page.wait_for_timeout(5000)

        # ===== 1. ищем активные дни =====
        days = page.query_selector_all("td, button, div")

        clickable_days = []

        for d in days:
            text = (d.inner_text() or "").strip()
            cls = (d.get_attribute("class") or "").lower()

            # день = цифра
            if not text.isdigit():
                continue

            # фильтр "активных" (гибкий, не ломается от верстки)
            if any(x in cls for x in [
                "active", "available", "select", "enabled", "click"
            ]):
                clickable_days.append(d)

        print(f"📅 found clickable days: {len(clickable_days)}")

        # ===== 2. кликаем дни и ищем время =====
        for d in clickable_days[:10]:  # ограничим, чтобы не долбить сайт
            try:
                d.click()
                page.wait_for_timeout(2000)

                # ищем время (как ты говорила — 12:00 появляется)
                times = page.query_selector_all("text=12:00")

                if times:
                    found_slots.append("12:00")

            except Exception as e:
                print("click error:", e)

        browser.close()

    return list(set(found_slots))


# ===== LOOP =====
def bot_loop():
    print("🚀 bot started")
    send_message("🚀 Бот запущен")

    last_sent = set()

    while True:
        try:
            print("🔁 checking calendar...")

            slots = check_slots()

            new_slots = [s for s in slots if s not in last_sent]

            if new_slots:
                msg = "🔥 Найдены слоты:\n" + "\n".join(new_slots)
                send_message(msg)

                last_sent.update(new_slots)

                print("SENT:", new_slots)
            else:
                print("😴 no slots")

        except Exception as e:
            print("💥 LOOP ERROR:", e)

        time.sleep(CHECK_EVERY)


# ===== START =====
threading.Thread(target=bot_loop, daemon=True).start()


# ===== KEEP ALIVE (Render) =====
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
