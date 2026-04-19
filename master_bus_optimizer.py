            bars[f'MA_{ma}'] = ta.sma(bars['close'], length=ma)
            bars['RSI'] = ta.rsi(bars['close'], length=14)
            macd = ta.macd(bars['close'], fast=12, slow=26, signal=9)
            bars['MACD_Line'] = macd['MACD_12_26_9']
            bars['MACD_Signal'] = macd['MACDs_12_26_9']

            balance = 10000
            asset_amount = 0
            in_trade = False

            # Run the track
            for i in range(max(ma_lengths), len(bars)):
                row = bars.iloc[i]
                prev_row = bars.iloc[i-1]

                macd_cross_up = prev_row['MACD_Line'] < prev_row['MACD_Signal'] and row['MACD_Line'] > row['MACD_Signal']

                # ENTRY
                if not in_trade and row['close'] > row[f'MA_{ma}'] and macd_cross_up and row['RSI'] < rsi_limit:
                    asset_amount = balance / row['open']
                    balance = 0
                    in_trade = True

                # EXIT
                if in_trade:
                    macd_cross_down = prev_row['MACD_Line'] > prev_row['MACD_Signal'] and row['MACD_Line'] < row['MACD_Signal']
                    if macd_cross_down or row['close'] < row[f'MA_{ma}'] or row['RSI'] >= rsi_limit:
                        balance = asset_amount * row['close']
                        asset_amount = 0
                        in_trade = False

            # Measure the mix
            final_val = balance + (asset_amount * bars.iloc[-1]['close'])
            roi = ((final_val - 10000) / 10000) * 100

            print(f"🎚️ Test Mix -> MA: {ma} | RSI Exit: {rsi_limit} | ROI: {roi:.2f}%")

            # Save the best sounding mix
            if roi > best_roi:
                best_roi = roi
                best_params = {'MA': ma, 'RSI_Exit': rsi_limit}

    print(f"\n🎧 THE ARTIST'S MIX FOUND FOR {symbol} 🎧")
    print(f"Best Compressor (MA): {best_params['MA']}-Day")
    print(f"Best Limiter (RSI): {best_params['RSI_Exit']}")
    print(f"Mastered ROI: {best_roi:.2f}%")

if __name__ == "__main__":
    sweep_the_eq("BTC/USD")