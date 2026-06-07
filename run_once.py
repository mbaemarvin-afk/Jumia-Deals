import os
import requests
import hashlib
import json
from bs4 import BeautifulSoup

# ----------------------------
# ENV VARIABLES
# ----------------------------
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
AFF_CODE = os.getenv("AFF_CODE", "")

BASE_URL = "https://www.jumia.co.ke"

CATEGORIES = [
    "electronics",
    "phones-tablets",
    "computing"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

SENT_FILE = "sent_deals.json"


# ----------------------------
# LOAD SENT DEALS
# ----------------------------
def load_sent():
    try:
        with open(SENT_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()


def save_sent(data):
    with open(SENT_FILE, "w") as f:
        json.dump(list(data), f)


# ----------------------------
# TELEGRAM
# ----------------------------
def send(msg):
    if not TOKEN or not CHAT_ID:
        print("❌ TELEGRAM_TOKEN or TELEGRAM_CHAT_ID missing")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    r = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
    )

    print("Telegram:", r.status_code, r.text)


# ----------------------------
# UNIQUE ID
# ----------------------------
def make_id(title, price):
    return hashlib.md5(
        f"{title}{price}".encode()
    ).hexdigest()


# ----------------------------
# SCRAPER
# ----------------------------
def scrape_category(category):

    url = f"{BASE_URL}/{category}/"

    print("Scraping:", url)

    try:
        r = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        print("Status:", r.status_code)

        soup = BeautifulSoup(r.text, "html.parser")

        products = []

        # More flexible selector
        cards = soup.find_all("article")

        print("Found cards:", len(cards))

        for card in cards:

            try:
                title_tag = card.find("h3")

                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)

                price_tag = card.find(class_="prc")

                if not price_tag:
                    continue

                price = price_tag.get_text(strip=True)

                link_tag = card.find("a", href=True)

                if not link_tag:
                    continue

                link = BASE_URL + link_tag["href"]

                products.append({
                    "title": title,
                    "price": price,
                    "url": link
                })

            except Exception as e:
                print("Item error:", e)

        return products

    except Exception as e:
        print("Scrape error:", e)
        return []


# ----------------------------
# MAIN
# ----------------------------
def run():

    print("🚀 Starting scrape")

    sent = load_sent()

    total_products = []

    for category in CATEGORIES:
        total_products.extend(
            scrape_category(category)
        )

    print("Products found:", len(total_products))

    # TEST MODE:
    # Send first 5 products regardless of discount

    sent_count = 0

    for p in total_products[:5]:

        deal_id = make_id(
            p["title"],
            p["price"]
        )

        if deal_id in sent:
            continue

        msg = f"""
🔥 <b>JUMIA DEAL</b>

📦 {p['title']}

💰 {p['price']}

🛒 {p['url']}
"""

        send(msg)

        sent.add(deal_id)

        sent_count += 1

    save_sent(sent)

    print("✅ Sent:", sent_count)


if __name__ == "__main__":
    run()