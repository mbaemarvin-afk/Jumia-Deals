import requests
import json
import hashlib
from bs4 import BeautifulSoup

# ----------------------------
# LOAD CONFIG
# ----------------------------
with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["TELEGRAM_TOKEN"]
CHAT_ID = config["TELEGRAM_CHAT_ID"]
AFF_CODE = config["AFF_CODE"]
BASE_URL = config["BASE_URL"]
CATEGORIES = config["CATEGORIES"]
HEADERS = config["HEADERS"]

SENT_FILE = "sent_deals.json"


# ----------------------------
# SAFE LOAD SENT
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


sent = load_sent()


# ----------------------------
# DEAL ID
# ----------------------------
def make_id(title, price):
    return hashlib.md5(f"{title}{price}".encode()).hexdigest()


# ----------------------------
# DISCOUNT CALC
# ----------------------------
def discount(old, new):
    try:
        return ((float(old) - float(new)) / float(old)) * 100
    except:
        return 0


# ----------------------------
# TELEGRAM
# ----------------------------
def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    })


# ----------------------------
# SCRAPE CATEGORY
# ----------------------------
def scrape_category(cat):
    url = f"{BASE_URL}{cat}/"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")

        products = []

        # Jumia product cards (common structure)
        items = soup.select("article.prd")

        for item in items:
            try:
                title = item.select_one("h3.name").text.strip()
                price_text = item.select_one("div.prc").text.replace("KSh", "").replace(",", "").strip()
                old_price_tag = item.select_one("div.old")
                link = item.select_one("a.core")["href"]

                price = float(price_text)
                old_price = float(old_price_tag.text.replace("KSh", "").replace(",", "").strip()) if old_price_tag else price

                products.append({
                    "title": title,
                    "price": price,
                    "old_price": old_price,
                    "url": "https://www.jumia.co.ke" + link
                })

            except:
                continue

        return products

    except Exception as e:
        print("Error scraping", cat, e)
        return []


# ----------------------------
# MAIN LOOP
# ----------------------------
all_products = []

for cat in CATEGORIES:
    print(f"Scraping {cat}...")
    all_products += scrape_category(cat)


# ----------------------------
# PROCESS & SEND
# ----------------------------
for p in all_products:

    d_id = make_id(p["title"], p["price"])

    # 🚫 duplicate check
    if d_id in sent:
        continue

    disc = discount(p["old_price"], p["price"])

    # 💰 only good deals
    if disc < 20:
        continue

    link = p["url"]
    if "?" in link:
        link += f"&affiliate_id={AFF_CODE}"
    else:
        link += f"?affiliate_id={AFF_CODE}"

    msg = f"""
🔥 <b>HOT DEAL</b>

📦 {p['title']}
💰 KSh {p['price']}
🏷 Old: KSh {p['old_price']}
📉 Save: {round(disc,1)}%

🛒 <a href="{link}">Buy Now</a>
"""

    send(msg)

    sent.add(d_id)


save_sent(sent)

print("✅ Scraping complete")