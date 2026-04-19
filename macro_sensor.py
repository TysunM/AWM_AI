import os
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta, timezone
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv

load_dotenv()
data_client = StockHistoricalDataClient(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'))

def get_market_regime():
    """
    CHAPTER 4: THE GLOBAL MACRO EYE.
    Analyzes the SPY to determine the Global Risk Multiplier.
    """
    print("🌍 AWM MACRO SENSOR: Analyzing Global Regime...")
    symbol = "SPY"

    try:
        end_ts = datetime.now(timezone.utc) - timedelta(minutes=20)
        req = StockBarsRequest(symbol_or_symbols=[symbol], timeframe=TimeFrame.Day, start=end_ts - timedelta(days=400), end=end_ts)
        df = data_client.get_stock_bars(req).df.loc[symbol]

        # Calculate the Global Shield
        df['sma_200'] = ta.sma(df['close'], length=200)
        current_price = df['close'].iloc[-1]
        market_sma = df['sma_200'].iloc[-1]

        if current_price > market_sma:
            return {"regime": "RISK_ON", "multiplier": 1.0, "status": "Bull Market"}
        else:
            return {"regime": "RISK_OFF", "multiplier": 0.5, "status": "Bear Market - Defense Only"}
    except Exception as e:
        print(f"❌ Macro Sensor Error: {e}")
        return {"regime": "UNKNOWN", "multiplier": 0.5, "status": "Caution"}