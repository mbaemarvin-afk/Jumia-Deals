import requests
import hashlib
import json
from bs4 import BeautifulSoup

# =====================================
# LOAD CONFIG
# =====================================

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

TOKEN = config["TELEGRAM_TOKEN"]
CHAT_ID = config["TELEGRAM_CHAT_ID"]
AFF_CODE = config["AFF_CODE"]

BASE_URL = "https://www.jumia.co.ke"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

CATEGORIES = [
    "phones-tablets",
    "computing",
    "televisions",
    "electronics"
]

SENT_FILE = "sent_deals.json"


# =====================================
# LOAD PREVIOUS POSTS
# =====================================

def load_sent():
    try:
        with open(SENT_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()


def save_sent(data):
    with open(SENT_FILE, "w") as f:
        json.dump(list(data), f)


# =====================================
# TELEGRAM
# =====================================

def send_telegram(message):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
    )

    print("Telegram:", response.status_code)

    if response.status_code == 200:
        return True

    print(response.text)
    return False


# =====================================
# UNIQUE ID
# =====================================

def make_id(title, price):

    return hashlib.md5(
        f"{title}{price}".encode()
    ).hexdigest()


# =====================================
# SCRAPER
# =====================================

def scrape_category(category):

    url = f"{BASE_URL}/{category}/"

    print(f"Scraping: {url}")

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        print("Status:", response.status_code)

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        cards = soup.find_all("article")

        print("Found cards:", len(cards))

        products = []

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

                product_url = (
                    BASE_URL +
                    link_tag["href"]
                )

                affiliate_url = (
                    product_url +
                    f"?aff_id={AFF_CODE}"
                )

                products.append({
                    "title": title,
                    "price": price,
                    "url": affiliate_url
                })

            except Exception as e:
                print("Product Error:", e)

        return products

    except Exception as e:

        print("Scrape Error:", e)
        return []


# =====================================
# MAIN
# =====================================

def run():

    print("🚀 Starting Jumia DealHunter")

    sent = load_sent()

    all_products = []

    for category in CATEGORIES:

        products = scrape_category(category)

        all_products.extend(products)

    print(
        f"Products found: {len(all_products)}"
    )

    sent_count = 0

    for product in all_products[:10]:

        deal_id = make_id(
            product["title"],
            product["price"]
        )

        if deal_id in sent:
            continue

        message = f"""
🔥 <b>JUMIA 14 YEARS NA WEWE DEAL</b>

📦 {product['title']}

💰 {product['price']}

🛒 Buy Now:
{product['url']}

⚡ Limited Stock
"""

        success = send_telegram(message)

        if success:

            sent.add(deal_id)

            sent_count += 1

    save_sent(sent)

    print(
        f"✅ Successfully sent {sent_count} deals"
    )


if __name__ == "__main__":
    run()