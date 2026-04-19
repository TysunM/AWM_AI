  GNU nano 7.2                                                                                    matrix_scanner.py
import os
import pandas as pd
from datetime import datetime, timedelta, timezone
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv

load_dotenv()
data_client = StockHistoricalDataClient(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'))

# The 11 Sector ETFs
SECTORS = {
    "XLK": "Technology", "XLF": "Financials", "XLV": "Healthcare",
    "XLY": "Consumer Discretionary", "XLI": "Industrials", "XLC": "Communication",
    "XLP": "Consumer Staples", "XLE": "Energy", "XLB": "Materials",
    "XLRE": "Real Estate", "XLU": "Utilities"
}

def get_sector_rankings():
    """
    CHAPTER 7: THE ALCHEMICAL MATRIX.
    Ranks sectors by 30-day Relative Strength.
    """
    print("📡 AWM MATRIX SCANNER: Ranking Sector Rotation...")
    rankings = []
    end_ts = datetime.now(timezone.utc) - timedelta(minutes=20)

    for symbol in SECTORS.keys():
        try:
            req = StockBarsRequest(symbol_or_symbols=[symbol], timeframe=TimeFrame.Day,
                                   start=end_ts - timedelta(days=45), end=end_ts)
            df = data_client.get_stock_bars(req).df.loc[symbol]

            # Calculate 30-day performance
            perf = (df['close'].iloc[-1] - df['close'].iloc[-30]) / df['close'].iloc[-30]
            rankings.append({"symbol": symbol, "name": SECTORS[symbol], "performance": perf})
        except: continue

    # Sort by strongest performance
    sorted_sectors = sorted(rankings, key=lambda x: x['performance'], reverse=True)
    top_3 = [s['name'] for s in sorted_sectors[:3]]

    print(f"🏆 Top Sectors: {', '.join(top_3)}")
    return sorted_sectors, top_3
