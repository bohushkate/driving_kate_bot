import time
import threading
from flask import Flask
from playwright.sync_api import sync_playwright

URL = "https://n170404.alteg.io/company/773361/personal/select-time?o=m2824298s10838308"

app = Flask(__name__)

last_result = {}


@app.route("/")
def home():
    return "Bot is alive"


@app.route("/ping")
def ping():
    return "pong"


def is_clickable_day(el):
    """
    Проверяем, что день реально активный (жирный/доступный)
    """
    try:
        if not el.is_visible() or not el.is_enabled():
            return False

        cls = (el.get_attribute("class") or "").lower()

        # типичные маркеры доступных дней
        if any(x in cls for x in ["disabled", "off", "past", "unavailable"]):
            return False

        # иногда доступные дни имеют data-атрибуты
        data = el.get_attribute("data-state") or ""
        if "disabled" in data:
            return False

        return True
    except:
        return False


def check_slots():
    global last_result

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        page = browser.new_page()

        try:
            print("🌐 Open calendar...")
            page.goto(URL, timeout=60000)

            page.wait_for_timeout(7000)
            page.wait_for_load_state("networkidle")

            # 🔥 ищем все элементы календаря
            days = page.locator("div, button, td").filter(has_text=r"^\d{1,2}$")

            count = days.count()
            print("📅 raw days:", count)

            available_days = []

            # ограничим чтобы не кликать 100 раз
            for i in range(min(count, 15)):
                el = days.nth(i)

                try:
                    text = el.inner_text().strip()

                    if not text.isdigit():
                        continue

                    # 🔥 ГЛАВНАЯ ПРОВЕРКА "ЖИРНЫЙ ДЕНЬ"
                    if not is_clickable_day(el):
                        continue

                    print(f"👉 clicking day {text}")
                    el.click()

                    # ждём появления слотов
                    page.wait_for_timeout(2500)

                    # ищем реальные времена
                    times = page.locator("text=/([01]?\\d|2[0-3]):[0-5]\\d/")

                    if times.count() > 0:
                        found_times = [t.inner_text() for t in times.all()]
                        print("⏰ TIMES:", found_times)

                        available_days.append({
                            "day": text,
                            "times": list(set(found_times))
                        })

                except Exception as e:
                    print("skip:", e)
                    continue

            last_result = {
                "status": "checked",
                "available": available_days,
                "found": len(available_days) > 0,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            print("✅ RESULT:", available_days)

        except Exception as e:
            last_result = {
                "status": "error",
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            print("❌ ERROR:", e)

        finally:
            browser.close()


def loop():
    while True:
        print("🔁 checking...")
        check_slots()
        time.sleep(120)


def start_thread():
    t = threading.Thread(target=loop, daemon=True)
    t.start()


if __name__ == "__main__":
    print("🚀 STARTING BOT LOOP")
    start_thread()
    app.run(host="0.0.0.0", port=10000)
