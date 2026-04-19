        for symbol, data in market_data.items():
            if current_date not in data['bars'].index: continue
            row_idx = data['bars'].index.get_loc(current_date)
            if row_idx < 1: continue
            curr, prev, params = data['bars'].iloc[row_idx], data['bars'].iloc[row_idx - 1], data['params']

            if symbol in positions:
                pos = positions[symbol]
                roi = (curr['close'] - pos['entry_price']) / pos['entry_price']
                trend_broken = (prev['MAC_L'] > prev['MAC_S'] and curr['MAC_L'] < curr['MAC_S']) or curr['close'] < curr['MA']

                exit_triggered = False
                # ATR Dynamic Leash (The 3x / 2x Rules)
                if (pos['entry_price'] - curr['close']) >= (curr['ATR'] * 3): exit_triggered = True
                elif trend_broken and (pos['entry_price'] - curr['close']) >= (curr['ATR'] * 2): exit_triggered = True
                elif curr['RSI'] >= params['RSI_Exit']: exit_triggered = True
                elif pos['status'] == 'ACTIVE' and trend_broken:
                    if roi > 0: exit_triggered = True
                    else: positions[symbol]['status'] = 'OBSERVING'
                elif pos['status'] == 'OBSERVING':
                    if roi >= 0.0: exit_triggered = True
                    elif not trend_broken: positions[symbol]['status'] = 'ACTIVE'

                if exit_triggered:
                    cash += pos['qty'] * curr['close']
                    if (curr['close'] - pos['entry_price']) > 0: wins += 1
                    else: losses += 1
                    trade_log.append(f"🔴 EXIT {symbol}: {'WIN' if (curr['close'] - pos['entry_price']) > 0 else 'LOSS'} ({roi*100:.1f}%)")
                    del positions[symbol]

            elif cash >= (current_equity * 0.20):
                if curr['close'] > curr['MA'] and (prev['MAC_L'] < prev['MAC_S'] and curr['MAC_L'] > curr['MAC_S']) and curr['RSI'] < params['RSI_Exit']:
                    qty = (current_equity * 0.20) // curr['close']
                    if qty > 0:
                        cash -= qty * curr['close']
                        positions[symbol] = {"qty": qty, "entry_price": curr['close'], "status": "ACTIVE"}
                        trade_log.append(f"🟢 ENTRY {symbol} @ ${curr['close']:.2f}")

    # --- 🏁 4. FINAL PERFORMANCE REPORT ---
    final_val = cash + sum(p['qty'] * market_data[s]['bars'].iloc[-1]['close'] for s, p in positions.items())
    print("\n" + "\n".join(trade_log[-15:]))
    print(f"\n{'='*60}")
    print(f"🏁 RESULTS FOR: {stance}")
    print(f"💰 Final Bank: ${final_val:,.2f} | ROI: {((final_val-100000)/100000)*100:.2f}%")
    print(f"📈 Wins: {wins} | 📉 Losses: {losses} | Total: {wins+losses}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    run_all_in_one()