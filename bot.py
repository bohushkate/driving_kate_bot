from flask import Flask, jsonify
from threading import Thread
from playwright.sync_api import sync_playwright
import time

URL = "https://n170404.alteg.io/company/773361/personal/select-time?o=m2824298s10838308"

app = Flask(__name__)

# сюда складываем найденные слоты
found_slots = []

# -------------------------
# FLASK
# -------------------------

@app.route("/")
def home():
    return "Bot is alive"

@app.route("/slots")
def slots():
    return jsonify(found_slots)


# -------------------------
# PLAYWRIGHT LOGIC
# -------------------------

def check_slots():
    global found_slots

    while True:
        try:
            print("🔁 checking slots...")

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto(URL, wait_until="networkidle")

                page.wait_for_timeout(5000)

                days = page.locator("td, .day, .calendar-day, [role='button']").all()

                print(f"📅 days found: {len(days)}")

                temp_slots = []

                for i in range(len(days)):
                    try:
                        days[i].click()
                        page.wait_for_timeout(2500)

                        times = page.locator("text=/\\b\\d{1,2}:\\d{2}\\b/").all_text_contents()

                        if times:
                            print("🔥 slots:", times)
                            temp_slots.extend(times)

                    except:
                        continue

                browser.close()

                if temp_slots:
                    found_slots = list(set(temp_slots))
                    print("✅ updated slots:", found_slots)
                else:
                    print("❌ no slots")

        except Exception as e:
            print("ERROR:", e)

        # пауза между проверками (чтобы не убить сайт и Render)
        time.sleep(60)


# -------------------------
# START BOT THREAD
# -------------------------

def start_thread():
    t = Thread(target=check_slots, daemon=True)
    t.start()


# -------------------------
# MAIN
# -------------------------

if __name__ == "__main__":
    print("🚀 STARTING BOT LOOP")
    start_thread()

    app.run(host="0.0.0.0", port=10000)
