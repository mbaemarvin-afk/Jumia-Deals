import time
import run_once

while True:
    print("⏰ Running scraper...")

    try:
        run_once.run()
    except Exception as e:
        print("Error:", e)

    print("😴 Sleeping for 1 hour...")
    time.sleep(3600)