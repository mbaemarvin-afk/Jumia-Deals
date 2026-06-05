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
AFF_CODE = os.getenv("AFF_CODE")

BASE_URL = "https://www.jumia.co.ke/"

CATEGORIES = [
    "electronics",
    "phones-tablets",
    "computing",
    "laptops",
    "home-living",
    "fashion-mens",
    "fashion-womens",
    "health-beauty",
    "kitchen-appliances",
    "sports-outdoor",
    "baby-products",
    "gaming",
    "televisions"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

SENT_FILE = "sent_deals.json"


# ----------------------------
# LOAD SENT DEALS
# ----------------------------
def load_sent():
    if not os.path.exists(SENT_FILE):
        return set()

    try:
        with open(SENT_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()


def save_sent(data):
    with open(SENT_FILE, "w") as f:
        json.dump(list(data), f)


# ----------------------------
# DEAL ID
# ----------------------------
def make_id(title, price):
    return hashlib.md5(f"{title}-{price}".encode()).hexdigest()


# ----------------------------
# DISCOUNT CALC
# ----------------------------
def discount(old, new):
    try:
        old = float(old)
        new = float(new)
        if old <= 0:
            return 0
        return ((old - new) / old) * 100
    except:
        return 0


# ----------------------------
# TELEGRAM SENDER
# ----------------------------
def send(msg):
    if not TOKEN or not CHAT_ID:
        print("❌ Missing Telegram env variables")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    try:
        r = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": msg,
                "parse_mode": "HTML"
            },
            timeout=10
        )
        print("Telegram response:", r.text)
    except Exception as e:
        print("Telegram error:", e)


# ----------------------------
# SCRAPER (FIXED + ROBUST)
# ----------------------------
def scrape_category(cat):
    url = f"{BASE_URL}{cat}/"

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        items = soup.select("article")
        products = []

        print(f"[{cat}] Items found:", len(items))

        for item in items:
            try:
                title_tag = item.select_one("h3, .name")
                price_tag = item.select_one(".prc")
                old_price_tag = item.select_one(".old")
                link_tag = item.select_one("a")

                if not title_tag or not price_tag or not link_tag:
                    continue

                title = title_tag.text.strip()

                price_text = price_tag.text.replace("KSh", "").replace(",", "").strip()
                price = float(price_text)

                old_price = price
                if old_price_tag:
                    try:
                        old_text = old_price_tag.text.replace("KSh", "").replace(",", "").strip()
                        old_price = float(old_text)
                    except:
                        pass

                link = link_tag.get("href", "")
                if not link.startswith("http"):
                    link = "https://www.jumia.co.ke" + link

                products.append({
                    "title": title,
                    "price": price,
                    "old_price": old_price,
                    "url": link
                })

            except:
                continue

        return products

    except Exception as e:
        print(f"Error scraping {cat}:", e)
        return []


# ----------------------------
# MAIN RUN
# ----------------------------
def run():
    sent = load_sent()

    all_products = []
    sent_count = 0

    print("🚀 Starting scrape...")

    for cat in CATEGORIES:
        print(f"Scraping: {cat}")
        all_products += scrape_category(cat)

    print("Total products collected:", len(all_products))

    for p in all_products:

        d_id = make_id(p["title"], p["price"])

        if d_id in sent:
            continue

        disc = discount(p["old_price"], p["price"])

        # 🔥 RELAXED FILTER (IMPORTANT FIX)
        if disc < 10:
            continue

        link = p["url"]
        if "?" in link:
            link += f"&affiliate_id={AFF_CODE}"
        else:
            link += f"?affiliate_id={AFF_CODE}"

        msg = f"""
🔥 <b>HOT DEAL ALERT</b>

📦 {p['title']}
💰 KSh {p['price']}
🏷 Old: KSh {p['old_price']}
📉 Save: {round(disc,1)}%

🛒 <a href="{link}">Buy Now</a>
"""

        send(msg)

        sent.add(d_id)
        sent_count += 1

    save_sent(sent)

    print(f"✅ Done. Sent {sent_count} deals")


# ----------------------------
# LOCAL TEST
# ----------------------------
if __name__ == "__main__":
    run()