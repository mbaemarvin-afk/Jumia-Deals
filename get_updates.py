import requests

TOKEN = "8502597717:AAEMjEhl28a6WYfsv9IetLRnQTvXhOBofPs"

url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

response = requests.get(url)

print(response.text)