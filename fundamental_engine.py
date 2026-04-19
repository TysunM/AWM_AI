import os
import requests
from dotenv import load_dotenv

load_dotenv()
FMP_API_KEY = os.getenv('FMP_API_KEY')

def analyze_fundamentals(symbol):
    """
    CHAPTER 3: THE FUNDAMENTAL ANCHOR.
    Calculates Quality based on EPS Growth and Margin Stability.
    """
    print(f"📊 JCA QUALITY AUDIT: Filtering {symbol}...")
    url = f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}?limit=2&apikey={FMP_API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()

        if len(data) < 2:
            return {"fund_score": 0, "status": "Trash/Insufficient Data", "quality_boost": 0}

        curr = data[0]
        prev = data[1]

        # 1. EPS Growth (The Apple Standard)
        eps_growth = (curr['eps'] - prev['eps']) / abs(prev['eps']) if prev['eps'] != 0 else 0

        # 2. Revenue Stability
        rev_growth = (curr['revenue'] - prev['revenue']) / prev['revenue']

        # 3. Margin Health
        margin = curr['grossProfit'] / curr['revenue']

        # Logic: We need to see positive momentum to get a score
        score = 0
        if eps_growth > 0.05: score += 1 # 5% EPS growth
        if rev_growth >= 0: score += 1    # Stable or growing revenue
        if margin > 0.25: score += 1     # Healthy 25% margin floor

        return {
            "fund_score": score,
            "eps_growth": eps_growth,
            "margin": margin,
            "quality_label": "High Quality" if score == 3 else "Speculative" if score == 2 else "Trash/Veto"
        }
    except Exception as e:
        print(f"❌ Fundamental Engine Error: {e}")
        return {"fund_score": 0, "quality_label": "Error/Veto"}
