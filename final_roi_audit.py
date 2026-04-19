    bars = data_client.get_stock_bars(StockBarsRequest(
        symbol_or_symbols=[symbol], timeframe=TimeFrame.Day, start=start, end=end
    )).df.loc[symbol]

    # 2. Indicators
    bars['ATR'] = ta.atr(bars['high'], bars['low'], bars['close'], length=14)
    bars['RSI'] = ta.rsi(bars['close'], length=14)
    bars['Vol_Avg'] = bars['volume'].rolling(window=20).mean()

    # 3. Strategy Variables
    balance = start_balance
    in_trade = False
    shares = 0
    entry_price = 0

    for i in range(1, len(bars)):
        row = bars.iloc[i]
        prev_row = bars.iloc[i-1]

        # ENTRY LOGIC (Alpha Slice)
        if not in_trade and prev_row['RSI'] < 45 and prev_row['volume'] > prev_row['Vol_Avg'] * 1.2:
            entry_price = row['open']
            shares = balance // entry_price
            balance -= (shares * entry_price)
            in_trade = True
            stop_loss = entry_price - (prev_row['ATR'] * 3)
            profit_target = entry_price + (prev_row['ATR'] * 3)

        # EXIT LOGIC (The Shield & The Harvest)
        if in_trade:
            # Shield Breach (Exit for Protection)
            if row['low'] <= stop_loss:
                balance += (shares * stop_loss)
                shares = 0
                in_trade = False
            # Harmonic Harvest (Take Profit)
            elif row['high'] >= profit_target:
                balance += (shares * profit_target)
                shares = 0
                in_trade = False

    final_val = balance + (shares * bars.iloc[-1]['close'])
    roi = ((final_val - start_balance) / start_balance) * 100
    print(f"--- 📈 {symbol} ROI REPORT ---")
    print(f"Final Balance: ${final_val:,.2f} | Total ROI: {roi:.2f}%")

if __name__ == "__main__":
    for ticker in ["AAPL", "NVDA", "TSLA"]:
        run_roi_simulation(ticker)