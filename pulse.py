import os, sqlite3, pandas as pd, requests
from alpaca.trading.client import TradingClient
from dotenv import load_dotenv

load_dotenv()
trading_client = TradingClient(os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_SECRET_KEY"), paper=True)

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