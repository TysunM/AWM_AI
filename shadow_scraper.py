import httpx
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def get_politician_trades():
    print("🕵️ SHADOW MODULE: Scanning Capitol Trades for political flow...")

    url = "https://www.capitoltrades.com/trades"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        with httpx.Client(headers=headers, follow_redirects=True) as client:
            response = client.get(url)

        if response.status_code != 200:
            print(f"❌ Shadow Error: Could not reach CapitolTrades (Status: {response.status_code})")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        # This targets the main trades table
        trades = []
        rows = soup.find_all('tr', class_='q-tr') # Target rows in their specific grid

        for row in rows[:20]: # Only look at the 20 most recent trades
            try:
                symbol = row.find('span', class_='q-field--issuer-ticker').text.strip()
                tx_type = row.find('span', class_='q-field--tx-type').text.strip()
                # Clean the symbol (sometimes they have :US or other suffixes)
                clean_symbol = symbol.split(':')[0]

                if tx_type.lower() == 'buy':
                    trades.append(clean_symbol)
            except AttributeError:
                continue

        unique_trades = list(set(trades))
        print(f"✅ SHADOW COMPLETE: Found {len(unique_trades)} recent political buys: {unique_trades}")
        return unique_trades

    except Exception as e:
        print(f"❌ SHADOW SCRAPER ERROR: {e}")
        return []

if __name__ == "__main__":
    get_politician_trades()