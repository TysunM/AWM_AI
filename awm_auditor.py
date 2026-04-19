import psycopg2
import pandas as pd
from datetime import datetime

def get_vault_connection():
    # Connects to your newly built AWM Vault
    return psycopg2.connect(
        dbname="alchemical_db",
        user="postgres",
        password="your_password", # Replace with your Postgres password if you set one
        host="localhost"
    )

def time_warp_audit():
    try:
        conn = get_vault_connection()
        # Pulls all open trades to analyze their temporal decay
        query = "SELECT symbol, entry_timestamp, trade_profile, entry_atr FROM positions WHERE status = 'open'"
        df = pd.read_sql(query, conn)

        if df.empty:
            print("🏛️ AWM Audit: The Vault is empty. No open positions to audit.")
            return

        for index, row in df.iterrows():
            hold_time = (datetime.now() - row['entry_timestamp']).days
            symbol = row['symbol']
            profile = row['trade_profile']

            print(f"Checking {symbol}: Held for {hold_time} days as a {profile}...")

            # Sprint Profile Logic (3-5 days max)
            if profile == 'Sprint' and hold_time >= 5:
                print(f"🚨 AWM ALERT: {symbol} exceeded Sprint time limit. Dead Money flagged for harvest.")

            # Marathon Profile Logic (20+ days max)
            elif profile == 'Marathon' and hold_time >= 20:
                print(f"🚨 AWM ALERT: {symbol} exceeded Marathon window. Dead Money flagged for harvest.")

        conn.close()
    except Exception as e:
        print(f"❌ Error accessing the Vault: {e}")

if __name__ == "__main__":
    print("Initiating Chapter 9: Time-Warp Audit...")
    time_warp_audit()