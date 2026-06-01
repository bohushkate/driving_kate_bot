import os
import time
import threading
from flask import Flask
from playwright.sync_api import sync_playwright

URL = "https://n170404.alteg.io/company/773361/personal/select-time?o=m2824298s10838308"

app = Flask(__name__)

# -------------------
# KEEP RENDER ALIVE
# -------------------
@app.route("/", methods=["GET", "HEAD"])
def home():
    return "OK", 200


# -------------------
# SLOT CHECKER
# -------------------
def check_slots():
    print("\n🧵 START SLOT CHECK")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 🔥 ловим все ответы API
        def handle_response(response):
            url = response.url.lower()

            if "time" in url or "slot" in url or "select" in url:
                print("\n📡 API CALL:", response.url)

                try:
                    data = response.json()
                    print("📦 JSON RESPONSE:")
                    print(data)
                except:
                    try:
                        print("📄 TEXT RESPONSE:")
                        print(response.text()[:500])
                    except:
                        pass

        page.on("response", handle_response)

        print("🌐 loading page...")
        page.goto(URL, timeout=60000)

        page.wait_for_timeout(5000)

        # -------------------
        # TRY CLICK FIRST DATE
        # -------------------
        try:
            print("📅 clicking first available date...")

            page.click("div[role='button']", timeout=5000)
        except:
            print("⚠️ no date clicked (selector may differ)")

        page.wait_for_timeout(8000)

        print("✅ DONE CHECK")

        browser.close()


# -------------------
# LOOP
# -------------------
def loop():
    print("🔥 BOT LOOP STARTED")

    while True:
        try:
            check_slots()
        except Exception as e:
            print("❌ ERROR:", e)

        time.sleep(60)


# -------------------
# START
# -------------------
if __name__ == "__main__":

    threading.Thread(target=loop, daemon=True).start()

    print("🚀 STARTING FLASK")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
