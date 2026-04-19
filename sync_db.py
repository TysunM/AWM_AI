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