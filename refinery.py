    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    bars = data_client.get_stock_bars(StockBarsRequest(
        symbol_or_symbols=[symbol], timeframe=TimeFrame.Day, start=start_date, end=end_date
    )).df.loc[symbol]

    # 2. Apply Chapter 8: Volatility Shield (3x ATR)
    bars['ATR'] = ta.atr(bars['high'], bars['low'], bars['close'], length=14)
    # The stop is based on the PREVIOUS day's close and ATR
    bars['Shield_Stop'] = bars['close'].shift(1) - (bars['ATR'].shift(1) * 3)

    # 3. Apply Chapter 9: Time-Warp (10-Day Opportunity Cost)
    # We flag periods where the price stayed within a 2% range for 10 days
    bars['Rolling_Max'] = bars['close'].rolling(window=10).max()
    bars['Rolling_Min'] = bars['close'].rolling(window=10).min()
    bars['Is_Zombie'] = (bars['Rolling_Max'] - bars['Rolling_Min']) / bars['Rolling_Min'] < 0.02

    # 4. Audit Results
    shakeouts = (bars['low'] < bars['Shield_Stop']).sum()
    zombie_periods = bars['Is_Zombie'].sum()

    print(f"--- 📊 {symbol} REFINERY REPORT ---")
    print(f"Total Trading Days: {len(bars)}")
    print(f"Shield Breaches (Losses): {shakeouts}")
    print(f"Zombie Days (Dead Money): {zombie_periods}")

    survival_rate = ((len(bars) - shakeouts) / len(bars)) * 100
    print(f"Sovereign Survival Rate: {survival_rate:.2f}%")

    if survival_rate < 90:
        print("⚠️ ACTION: Volatility is too high. Widen the Shield to 3.5x ATR.")
    else:
        print("✅ ACTION: Shield is optimal. Strategy is robust.")

    # 5. Apply Chapter 3 & 5: The Alpha Slice (Entry Logic)
    bars['RSI'] = ta.rsi(bars['close'], length=14)
    bars['Volume_SMA'] = bars['volume'].rolling(window=20).mean()

    # Logic: Only enter if RSI is low (Oversold) AND Volume is higher than average (Whale activity)
    bars['Ideal_Entry'] = (bars['RSI'] < 45) & (bars['volume'] > bars['Volume_SMA'] * 1.2)

    entries_found = bars['Ideal_Entry'].sum()
    print(f"Alpha Entry Signals Found: {entries_found}")

if __name__ == "__main__":
    # Test the core portfolio candidates
    for ticker in ["AAPL", "NVDA", "TSLA"]:
        run_refinery_audit(ticker)
