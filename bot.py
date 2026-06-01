from flask import Flask, jsonify
from playwright.sync_api import sync_playwright
import threading

URL = "https://n170404.alteg.io/company/773361/personal/select-time?o=m2824298s10838308"

app = Flask(__name__)

def get_slots():
    slots = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        def handle_response(response):
            try:
                if "slot" in response.url or "time" in response.url:
                    data = response.json()
                    print("FOUND API:", response.url)

                    # пробуем вытащить слоты из разных структур
                    if isinstance(data, dict):
                        for key in ["slots", "data", "times", "available"]:
                            if key in data:
                                slots.append(data[key])

            except:
                pass

        page.on("response", handle_response)

        page.goto(URL, wait_until="networkidle")

        # ждём JS догрузку
        page.wait_for_timeout(8000)

        html = page.content()

        browser.close()

    return {
        "slots": slots,
        "html_snippet": html[:500]
    }


@app.route("/")
def home():
    return "BOT IS ALIVE"

@app.route("/slots")
def slots():
    return jsonify(get_slots())


def run_bot():
    print("🚀 STARTING BOT LOOP")
    while True:
        try:
            get_slots()
        except Exception as e:
            print("ERROR:", e)


if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
