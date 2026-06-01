from flask import Flask, jsonify
from threading import Thread
from playwright.sync_api import sync_playwright
import time

# ----- URL = "https://n170404.alteg.io/company/773361/personal/select-time?o=m3031495s10838308"
URL = "https://n170404.alteg.io/company/773361/personal/select-time?o=m2824298s10838308"

app = Flask(__name__)

status = {
    "has_slots": False,
    "message": "not checked yet"
}


# ---------------- FLASK ----------------

@app.route("/")
def home():
    return "bot alive"

@app.route("/status")
def get_status():
    return jsonify(status)


# ---------------- CHECKER ----------------

def check_loop():
    global status

    while True:
        try:
            print("🔁 checking calendar...")

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto(URL, wait_until="networkidle")
                page.wait_for_timeout(5000)

                # 🔥 ключевой момент: жирные даты (обычно bold / active / available)
                bold_days = page.locator("b, strong, .bold, .active, .available").all_text_contents()

                # чистим мусор
                bold_days = [d.strip() for d in bold_days if d.strip()]

                print("FOUND BOLD:", bold_days)

                if bold_days:
                    status["has_slots"] = True
                    status["message"] = f"🔥 AVAILABLE DAYS: {bold_days}"
                else:
                    status["has_slots"] = False
                    status["message"] = "no slots"

                browser.close()

        except Exception as e:
            status["has_slots"] = False
            status["message"] = f"error: {e}"
            print("ERROR:", e)

        time.sleep(60)


# ---------------- START ----------------

def start_thread():
    t = Thread(target=check_loop, daemon=True)
    t.start()


if __name__ == "__main__":
    print("🚀 bot started")
    start_thread()
    app.run(host="0.0.0.0", port=10000)
