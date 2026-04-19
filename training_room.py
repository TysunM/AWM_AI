from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
data_client = StockHistoricalDataClient(os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_SECRET_KEY"))
PRESET_FILE = "master_presets.json"
HEDGE_LIST = ["SH", "PSQ"]

class UnifiedTrainingRoom:
    def __init__(self):
        self.ma_settings, self.atr_settings, self.equity = [20, 50, 100], [1.5, 2.0, 3.0], 100000.00

    def run_sim(self, bars, ma, atr):
        cash, qty, entry = self.equity, 0, 0
        bars = bars.copy()
        bars["MA"] = ta.sma(bars["close"], length=ma)
        bars["ATR"] = ta.atr(bars["high"], bars["low"], bars["close"], length=14)
        for i in range(1, len(bars)):
            c = bars.iloc[i]
            if pd.isna(c["MA"]): continue
            if qty > 0:
                if (entry - c["close"]) >= (c["ATR"] * atr) or c["close"] < c["MA"]:
                    cash += qty * c["close"]; qty = 0
            elif c["close"] > c["MA"]:
                qty = (cash * 0.02) // c["close"]
                if qty > 0: entry, cash = c["close"], cash - (qty * c["close"])
        return ((cash + (qty * bars.iloc[-1]["close"]) - self.equity) / self.equity) * 100

    def execute(self):
        print("🧪 TRAINING START...")
        with open(PRESET_FILE, "r") as f: vips = json.load(f)
        for h in HEDGE_LIST: vips[h] = vips.get(h, {})
        for sym in list(vips.keys()):
            try:
                df = data_client.get_stock_bars(StockBarsRequest(symbol_or_symbols=[sym], timeframe=TimeFrame.Day, start=datetime.now()-timedelta(days=365), end=datetime.now())).df.loc[sym]
                best_roi, best_c = -999, {}
                for m in self.ma_settings:
                    for a in self.atr_settings:
                        roi = self.run_sim(df, m, a)
                        if roi > best_roi: best_roi, best_c = roi, {"MA": m, "ATR": a, "RSI_Exit": 75}
                if best_c: vips[sym].update(best_c); print(f"✅ {sym} Optimized.")
            except: continue
        with open(PRESET_FILE, "w") as f: json.dump(vips, f, indent=4)

if __name__ == "__main__":
    UnifiedTrainingRoom().execute()