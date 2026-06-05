from flask import Flask
import threading
import time
import run_once

app = Flask(__name__)

# ----------------------------
# HEALTH CHECK (UptimeRobot)
# ----------------------------
@app.route("/")
def home():
    return "🚀 Jumia Bot is running"

# ----------------------------
# MANUAL TRIGGER (TEST)
# ----------------------------
@app.route("/run")
def run_now():
    try:
        run_once.run()
        return "✅ Scraper executed"
    except Exception as e:
        return f"❌ Error: {e}"

# ----------------------------
# BACKGROUND SCHEDULER
# ----------------------------
def scheduler():
    while True:
        try:
            print("⏰ Running scheduled scrape...")
            run_once.run()
        except Exception as e:
            print("Scheduler error:", e)

        time.sleep(3600)  # 1 hour

# ----------------------------
# START BACKGROUND THREAD
# ----------------------------
threading.Thread(target=scheduler, daemon=True).start()

# ----------------------------
# START SERVER
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)