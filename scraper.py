import requests
from bs4 import BeautifulSoup
import json
import random

cfg = json.load(open("config.json"))

BASE_URL = cfg["BASE_URL"]
CATEGORIES = cfg["CATEGORIES"]

def get_deals():
    category = random.choice(CATEGORIES)
    url = f"{BASE_URL}{category}/"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    products = soup.select("article.prd")

    deals = []

    for p in products[:10]:
        name = p.select_one("h3")
        price = p.select_one(".prc")
        link = p.select_one("a")

        if name and price and link:
            deals.append({
                "name": name.text,
                "price": price.text,
                "link": BASE_URL + link["href"]
            })

    return deals