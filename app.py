from flask import Flask
import threading
import time
import run_once  # we will refactor logic into it

app = Flask(__name__)

# ----------------------------
# HEALTH CHECK (for UptimeRobot)
# ----------------------------
@app.route("/")
def home():
    return "Jumia Bot is running ✅"

@app.route("/run")
def run_now():
    run_once.main()
    return "Scraper executed ✅"


# ----------------------------
# BACKGROUND SCHEDULER
# ----------------------------
def scheduler():
    while True:
        try:
            run_once.main()
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