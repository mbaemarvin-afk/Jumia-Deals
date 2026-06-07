import requests
import json

with open("config.json", "r") as f:
    config = json.load(f)

token = config["TELEGRAM_TOKEN"]
chat_id = config["TELEGRAM_CHAT_ID"]

message = "🔥 Deal Hunter Test Message"

url = f"https://api.telegram.org/bot{token}/sendMessage"

payload = {
    "chat_id": chat_id,
    "text": message
}

response = requests.post(url, data=payload)

print(response.text)python test_telegram.py