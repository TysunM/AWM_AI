import pandas_ta as ta

def analyze_asset(df):
    """
    CHAPTER 8 UPGRADE: Now calculates ATR for the Volatility Shield.
    """
    # ... (Existing Technical Logic) ...

    # Calculate 14-day ATR
    df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
    latest_atr = df['atr'].iloc[-1]
    latest_price = df['close'].iloc[-1]

    # Calculate the Shield Level (3x ATR below current price)
    shield_level = latest_price - (latest_atr * 3)

    return {
        "latest_price": latest_price,
        "atr": latest_atr,
        "shield_level": shield_level,
        "conviction_score": 7, # Placeholder for your existing scoring
        "rationales": ["Above 200 SMA", "Volatility Shield Calculated"]
    }
