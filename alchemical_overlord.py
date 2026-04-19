                self.conn.execute("DELETE FROM live_positions WHERE symbol=?", (p.symbol,))
            except: continue
        self.conn.commit()

    def get_market_regime(self):
        try:
            end = datetime.now()
            spy = data_client.get_stock_bars(StockBarsRequest(symbol_or_symbols=["SPY"], timeframe=TimeFrame.Day, start=end - timedelta(days=50), end=end)).df.loc["SPY"]
            mom = ((spy["close"].iloc[-1] - spy["close"].iloc[20]) / spy["close"].iloc[20]) * 100
            if mom > 3.0: return "BULL", 0.05
            if mom < -3.0: return "BEAR", 0.03
            return "CHOP", 0.02
        except: return "UNKNOWN", 0.01

    def execute(self):
        self.check_solvency()
        regime, risk_cap = self.get_market_regime()
        print(f"🏛️ REGIME: {regime} | EQUITY: \${self.equity:,.2f} | CASH: \${self.cash:,.2f}")
        with open(PRESET_FILE, "r") as f: vips = json.load(f)
        watchlist = {t: {"MA": 20, "ATR": 1.5, "RSI_Exit": 70} for t in HEDGE_LIST} if regime == "BEAR" else {k: v for k, v in vips.items() if "MA" in v}
        can_buy = self.cash > (self.equity * 0.1)

        for symbol, params in watchlist.items():
            try:
                bars = data_client.get_stock_bars(StockBarsRequest(symbol_or_symbols=[symbol], timeframe=TimeFrame.Day, start=datetime.now() - timedelta(days=120), end=datetime.now())).df.loc[symbol]
                macd = ta.macd(bars["close"])
                bars["MAC_L"], bars["MAC_S"] = macd.iloc[:,0], macd.iloc[:,2]
                bars["ATR"], bars["RSI"] = ta.atr(bars["high"], bars["low"], bars["close"], length=14), ta.rsi(bars["close"], length=14)
                bars["MA"], bars["VOL_MA"] = ta.sma(bars["close"], length=params["MA"]), ta.sma(bars["volume"], length=20)
                curr, prev = bars.iloc[-1], bars.iloc[-2]
                trade = self.conn.execute("SELECT * FROM live_positions WHERE symbol=?", (symbol,)).fetchone()

                if trade:
                    _, entry, qty, max_s, _ = trade
                    if curr["close"] > max_s: self.conn.execute("UPDATE live_positions SET max_seen=? WHERE symbol=?", (curr["close"], symbol))
                    if (entry - curr["close"]) >= (curr["ATR"] * params.get("ATR", 2.0)) or curr["close"] < curr["MA"]:
                        trading_client.submit_order(MarketOrderRequest(symbol=symbol, qty=qty, side=OrderSide.SELL, time_in_force=TimeInForce.DAY))
                        self.conn.execute("DELETE FROM live_positions WHERE symbol=?", (symbol,))
                elif can_buy:
                    if (curr["close"] > curr["MA"]) and (curr["MAC_L"] > curr["MAC_S"]) and (curr["volume"] > curr["VOL_MA"] * 1.25):
                        qty = int((self.equity * risk_cap) // curr["close"])
                        if qty > 0:
                            trading_client.submit_order(MarketOrderRequest(symbol=symbol, qty=qty, side=OrderSide.BUY, time_in_force=TimeInForce.DAY))
                            self.conn.execute("INSERT INTO live_positions VALUES (?, ?, ?, ?, ?)", (symbol, curr["close"], qty, curr["close"], datetime.now().strftime("%Y-%m-%d")))
                self.conn.commit()
            except: continue

if __name__ == "__main__":
    AlchemicalOverlord().execute()
