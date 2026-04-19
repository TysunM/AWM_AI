class AlchemicalPulse:
    def __init__(self):
        self.conn = sqlite3.connect("sovereign.db")
        acc = trading_client.get_account()
        self.equity, self.cash = float(acc.equity), float(acc.cash)

    def dispatch(self, msg):
        url = os.getenv("WEBHOOK_URL")
        if url: requests.post(url, data=msg.encode("utf-8"), headers={"Title": "AWM Pulse", "Tags": "moneybag"})

    def get_vitals(self):
        pos = trading_client.get_all_positions()
        report = [f"Equity: \${self.equity:,.2f} | Cash: \${self.cash:,.2f}", "-"*20]
        for p in pos:
            report.append(f"{p.symbol}: {float(p.unrealized_intraday_plpc)*100:>+4.1f}%")
        final = "\\n".join(report)
        print(final); self.dispatch(final)

if __name__ == "__main__":
    AlchemicalPulse().get_vitals()
INNER_EOF

# 4. Helpers & Config
cat << 'INNER_EOF' > sync_db.py
import os, sqlite3, datetime
from alpaca.trading.client import TradingClient
from dotenv import load_dotenv
load_dotenv()
tc = TradingClient(os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_SECRET_KEY"), paper=True)
conn = sqlite3.connect("sovereign.db")
conn.execute("DELETE FROM live_positions")
for p in tc.get_all_positions():
    conn.execute("INSERT INTO live_positions VALUES (?,?,?,?,?)", (p.symbol, float(p.avg_entry_price), float(p.qty), float(p.current_price), datetime.datetime.now().strftime("%Y-%m-%d")))
conn.commit()
print("✅ DB Synced.")
INNER_EOF

cat << 'INNER_EOF' > master_presets.json
{"AAPL": {}, "MSFT": {}, "NVDA": {}, "TSLA": {}, "META": {}, "GOOGL": {}, "AMZN": {}, "AMD": {}, "NFLX": {}, "AVGO": {}, "SH": {}, "PSQ": {}}
INNER_EOF

echo "pandas" > requirements.txt
echo "pandas_ta" >> requirements.txt
echo "alpaca-py" >> requirements.txt
echo "python-dotenv" >> requirements.txt
echo "requests" >> requirements.txt

chmod +x *.py
echo "🚀 Rebuild complete. Files created."