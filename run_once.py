import json
from scraper import get_deals

# IMPORT YOUR TELEGRAM FUNCTION HERE
# from telegram_bot import send_to_telegram

def run():
    print("🚀 Starting scrape...")

    deals = get_deals()

    print(f"Products found: {len(deals)}")

    if not deals:
        print("No deals found.")
        return

    for deal in deals:
        message = f"""
🔥 JUMIA DEAL

📦 {deal['name']}
💰 {deal['price']}
🔗 {deal['link']}
"""

        print(message)

        # SEND TO TELEGRAM (uncomment when ready)
        # send_to_telegram(message)

    print("✅ Run completed")