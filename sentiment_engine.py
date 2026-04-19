import os
from textblob import TextBlob
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestNewsRequest
from dotenv import load_dotenv

load_dotenv()
data_client = StockHistoricalDataClient(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'))

def get_detailed_sentiment(symbol):
    """
    CHAPTER 2 UPGRADE: Analyzes both positive and negative angles.
    """
    try:
        req = StockLatestNewsRequest(symbol_or_symbols=[symbol], limit=15)
        news_data = data_client.get_news(req)
        if not news_data.news: return 0.0, "Neutral", "None detected"

        headlines = [n.headline for n in news_data.news]

        bullish_points = []
        bearish_points = []

        for h in headlines:
            score = TextBlob(h).sentiment.polarity
            if score > 0.1: bullish_points.append(h)
            elif score < -0.1: bearish_points.append(h)

        overall_score = TextBlob(" ".join(headlines)).sentiment.polarity

        # Summary for the Prospectus
        bear_case = bearish_points[0] if bearish_points else "No immediate negative news friction."
        bull_case = bullish_points[0] if bullish_points else "No immediate positive news drivers."

        return overall_score, bull_case, bear_case
    except:
        return 0.0, "N/A", "N/A"