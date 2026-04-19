        with open(PRESET_FILE, 'r') as f: vips = json.load(f)
        watchlist = HEDGE_LIST if regime == "BEAR" else [k for k, v in vips.items() if 'Time_Stop' in v]

        for symbol in watchlist:
            try:
                params = vips.get(symbol, {'MA': 50, 'ATR': 2.0, 'RSI_Exit': 75, 'Time_Stop': 10})
                w_bars = data_client.get_stock_bars(StockBarsRequest(symbol_or_symbols=[symbol], timeframe=TimeFrame.Week, start=start_dt - timedelta(weeks=52), end=end_dt)).df.loc[symbol]
                w_ma = ta.sma(w_bars['close'], length=20)

                bars = data_client.get_stock_bars(StockBarsRequest(symbol_or_symbols=[symbol], timeframe=TimeFrame.Day, start=start_dt - timedelta(days=150), end=end_dt)).df.loc[symbol]
                macd = ta.macd(bars['close'])
                bars['MAC_L'], bars['MAC_S'] = macd.iloc[:,0], macd.iloc[:,2]
                bars['ATR'], bars['RSI'] = ta.atr(bars['high'], bars['low'], bars['close'], length=14), ta.rsi(bars['close'], length=14)
                bars['MA'], bars['VOL_MA'] = ta.sma(bars['close'], length=params['MA']), ta.sma(bars['volume'], length=20)

                sim_bars = bars[bars.index >= pd.to_datetime(start_dt).tz_localize('UTC')]
                qty, entry_price, days_in = 0, 0, 0

                for i in range(1, len(sim_bars)):
                    curr, prev = sim_bars.iloc[i], sim_bars.iloc[i-1]
                    if pd.isna(curr['MA']) or pd.isna(curr['ATR']): continue

                    if qty > 0:
                        days_in += 1
                        exit_r = None
                        if (entry_price - curr['close']) >= (curr['ATR'] * params['ATR']): exit_r = "ATR Stop"
                        elif ((prev['MAC_L'] > prev['MAC_S'] and curr['MAC_L'] < curr['MAC_S']) or curr['close'] < curr['MA']) and (entry_price - curr['close']) >= (curr['ATR'] * (params['ATR'] * 0.66)): exit>
                        elif curr['RSI'] >= params['RSI_Exit']: exit_r = "RSI Peak"
                        elif days_in >= params['Time_Stop'] and ((curr['close'] - entry_price) / entry_price) < 0.02: exit_r = "Time Stop"

                        if exit_r:
                            pnl = (curr['close'] - entry_price) * qty
                            self.wins += 1 if pnl > 0 else 0
                            self.losses += 1 if pnl <= 0 else 0
                            self.ledger.append({'date': sim_bars.index[i].strftime('%Y-%m-%d'), 'symbol': symbol, 'pnl': pnl, 'reason': exit_r})
                            qty = 0
                    else:
                        anchor_ok = w_ma.loc[:sim_bars.index[i]].iloc[-1] > w_ma.loc[:sim_bars.index[i]].iloc[-2]
                        if (curr['close'] > curr['MA']) and (curr['MAC_L'] > curr['MAC_S']) and (curr['volume'] > curr['VOL_MA'] * 1.25) and anchor_ok:
                            qty = (self.starting_bank * 0.03) // curr['close']
                            entry_price, days_in = curr['close'], 0
            except: continue

        gross = sum(item['pnl'] for item in self.ledger)
        print(f"🏁 SIM COMPLETE | WINS: {self.wins} | LOSSES: {self.losses} | P&L: ${gross:,.2f}")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    SovereignSimulator().execute()