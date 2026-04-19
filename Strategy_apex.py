    start = end - timedelta(days=150)

    for symbol, params in vips.items():
        try:
            bars = data_client.get_stock_bars(StockBarsRequest(
                symbol_or_symbols=[symbol], timeframe=TimeFrame.Day, start=start, end=end
            )).df.loc[symbol]

            # Analysis
            bars['MA'] = ta.sma(bars['close'], length=params['MA'])
            bars['RSI'] = ta.rsi(bars['close'], length=14)
            macd = ta.macd(bars['close'], fast=12, slow=26, signal=9)
            bars['MAC_L'] = macd['MACD_12_26_9']
            bars['MAC_S'] = macd['MACDs_12_26_9']

            row = bars.iloc[-1]
            prev = bars.iloc[-2]

            # Position Check
            positions = trading_client.get_all_positions()
            in_trade = any(p.symbol == symbol for p in positions)

            # --- LOGIC GATE 1: EXIT (Always Priority) ---
            if in_trade:
                if (prev['MAC_L'] > prev['MAC_S'] and row['MAC_L'] < row['MAC_S']) or \
                   (row['close'] < row['MA']) or \
                   (row['RSI'] >= params['RSI_Exit']):
                    log_vault(f"🔴 EXITING: {symbol} @ {row['close']:.2f}")
                    trading_client.close_position(symbol)

            # --- LOGIC GATE 2: ENTRY (Only if Healthy & Zen) ---
            elif not in_trade and not is_bank_sick and final_conviction_cap > 0:
                if row['close'] > row['MA'] and \
                   (prev['MAC_L'] < prev['MAC_S'] and row['MAC_L'] > row['MAC_S']) and \
                   (row['RSI'] < params['RSI_Exit']):

                    # Size based on Karma-Adjusted Cap
                    qty = (total_equity * final_conviction_cap) // row['close']
                    if qty > 0:
                        log_vault(f"🟢 ENTERING: {symbol} @ {row['close']:.2f} (Using {final_conviction_cap*100:.1f}% Cap)")
                        trading_client.submit_order(MarketOrderRequest(
                            symbol=symbol, qty=qty, side=OrderSide.BUY, time_in_force=TimeInForce.DAY
                        ))

        except Exception as e:
            continue

if __name__ == "__main__":
    execute_apex_harvest()