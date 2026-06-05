import os
import threading
import time
import subprocess
from flask import Flask, jsonify

def background_worker():
    time.sleep(5)
    while True:
        subprocess.run(["python", "auto_poster.py"])
        time.sleep(3600)

t = threading.Thread(target=background_worker, daemon=True)
t.start()

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
