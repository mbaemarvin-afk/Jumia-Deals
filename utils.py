import hashlib
import json
import os

SENT_FILE = "sent_deals.json"


# ----------------------------
# LOAD SENT DEALS
# ----------------------------
def load_sent():
    if not os.path.exists(SENT_FILE):
        return set()

    with open(SENT_FILE, "r") as f:
        return set(json.load(f))


# ----------------------------
# SAVE SENT DEALS
# ----------------------------
def save_sent(sent_set):
    with open(SENT_FILE, "w") as f:
        json.dump(list(sent_set), f)


# ----------------------------
# CREATE UNIQUE ID FOR PRODUCT
# ----------------------------
def make_deal_id(title, price):
    raw = f"{title}-{price}"
    return hashlib.md5(raw.encode()).hexdigest()


# ----------------------------
# DISCOUNT FILTER (20%+)
# ----------------------------
def is_good_deal(old_price, new_price, min_discount=20):
    try:
        old_price = float(old_price)
        new_price = float(new_price)

        if old_price <= 0:
            return False

        discount = ((old_price - new_price) / old_price) * 100
        return discount >= min_discount

    except:
        return False


# ----------------------------
# CLEAN AFFILIATE LINK
# ----------------------------
def build_affiliate_link(base_url, aff_code):
    if "?" in base_url:
        return f"{base_url}&affiliate_id={aff_code}"
    return f"{base_url}?affiliate_id={aff_code}"