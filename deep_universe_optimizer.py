                for rsi_limit in rsi_exits:
                    balance = 10000
                    asset_amount = 0
                    in_trade = False

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

                    final_val = balance + (asset_amount * bars.iloc[-1]['close'])
                    roi = ((final_val - 10000) / 10000) * 100

                    if roi > best_roi:
                        best_roi = roi
                        best_params = {'MA': ma, 'RSI_Exit': rsi_limit, 'Mastered_ROI': round(roi, 2)}

            preset_library[symbol] = best_params
            print(f"⭐ PERFECT TAKE FOUND -> MA: {best_params['MA']} | RSI: {best_params['RSI_Exit']} | ROI: {best_params['Mastered_ROI']}%")

            time.sleep(0.5)

        except Exception as e:
            print(f"⚠️ Track Corrupted (Skipping {symbol}): {e}")

    # Save the ultimate compilation
    preset_path = '/root/alchemical_engine/master_presets.json'
    with open(preset_path, 'w') as f:
        json.dump(preset_library, f, indent=4)

    print(f"\n💾 THE ALBUM IS MASTERED. Presets saved to: {preset_path}")

if __name__ == "__main__":
    run_deep_compilation()