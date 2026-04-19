from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
FMP_API_KEY = os.getenv('FMP_API_KEY')

def get_whale_velocity_signal(symbol):
    """
    CHAPTER 5: FLOW VELOCITY.
    Analyzes fresh institutional prints with Time Decay.
    """
    print(f"🐋 AWM WHALE SENSOR: Measuring Flow Velocity for {symbol}...")
    url = f"https://financialmodelingprep.com/api/v4/institutional-ownership/symbol-ownership?symbol={symbol}&apikey={FMP_API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()

        if not data or not isinstance(data, list):
            return {"whale_score": 0, "velocity_label": "Static"}

        # Chapter 5 Logic: Freshness Matters
        current_year = datetime.now().year
        fresh_buys = 0
        total_change = 0

        for record in data[:15]: # Look at the last 15 filings
            filing_date = record.get('reportDate', "")
            change = record.get('change', 0)

            # If the filing is from the current or previous quarter, it's "Fresh"
            is_fresh = str(current_year) in filing_date

            if change > 0:
                # Fresh buys get a 2x multiplier in our logic
                fresh_buys += (2 if is_fresh else 1)
                total_change += change

        # Velocity Labeling
        if fresh_buys >= 10:
            return {"whale_score": 3, "velocity_label": "High Urgency (Whale Breach)"}
        elif fresh_buys >= 5:
            return {"whale_score": 2, "velocity_label": "Steady Accumulation"}
        else:
            return {"whale_score": 0, "velocity_label": "Low Flow"}

    except Exception as e:
        print(f"❌ Whale Velocity Error: {e}")
        return {"whale_score": 0, "velocity_label": "Error"}