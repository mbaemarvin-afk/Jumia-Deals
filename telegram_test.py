import requests
import json

with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["TELEGRAM_TOKEN"]
CHAT_ID = config["TELEGRAM_CHAT_ID"]

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": "🔥 DealHunter Test Message"
}

response = requests.post(url, data=payload)

print(response.text)