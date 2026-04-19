
                        # Deep Vision Logic
                        if current_drop >= (curr['ATR'] * atr_mult):
                            exit_triggered = True
                        elif trend_broken and current_drop >= (curr['ATR'] * (atr_mult * 0.66)):
                            exit_triggered = True
                        elif curr['RSI'] >= rsi_ext:
                            exit_triggered = True
                        elif status == 'ACTIVE':
                            if trend_broken:
                                if current_roi > 0: exit_triggered = True
                                else: status = 'OBSERVING'
                        elif status == 'OBSERVING':
                            if current_roi >= 0.0: exit_triggered = True
                            elif not trend_broken: status = 'ACTIVE'

                        if exit_triggered:
                            cash += qty * curr['close']
                            qty = 0
                            status = 'FLAT'

                    elif not in_trade:
                        if curr['close'] > curr['MA'] and (prev['MAC_L'] < prev['MAC_S'] and curr['MAC_L'] > curr['MAC_S']) and curr['RSI'] < rsi_ext:
                            trade_alloc = cash * 0.20 # 20% Rule remains ironclad
                            qty = trade_alloc // curr['close']
                            if qty > 0:
                                entry_price = curr['close']
                                cash -= (qty * entry_price)
                                status = 'ACTIVE'

                # Final timeline accounting
                if qty > 0: cash += qty * test_df.iloc[-1]['close']
                roi = ((cash - 100000.0) / 100000.0) * 100

                results.append({
                    'MA': ma, 'ATR_Mult': atr_mult, 'RSI_Exit': rsi_ext, 'ROI': roi, 'Final_Bank': cash
                })

    # Output the absolute best setups
    results.sort(key=lambda x: x['ROI'], reverse=True)
    print("\n🏆 TOP 3 OPTIMIZED CONFIGURATIONS (5-YEAR TIMELINE)")
    print("-" * 60)
    for idx, r in enumerate(results[:3]):
        print(f"#{idx+1} | MA: {r['MA']} | ATR Leash: {r['ATR_Mult']}x | RSI Ceiling: {r['RSI_Exit']} ==> ROI: {r['ROI']:.2f}%")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    target = sys.argv[1].upper() if len(sys.argv) > 1 else "TSLA"
    run_matrix(target)
