load_dotenv()
crypto_client = CryptoHistoricalDataClient(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'))

def run_bitcoin_sovereign_audit(start_balance=10000):
    print(f"🪙 REFINING: Bitcoin 'Digital Gold' (Deep Value Audit)...")

    end = datetime.now() - timedelta(minutes=20)
    start = end - timedelta(days=730)

    bars = crypto_client.get_crypto_bars(CryptoBarsRequest(
        symbol_or_symbols=["BTC/USD"], timeframe=TimeFrame.Day, start=start, end=end
    )).df.loc["BTC/USD"]

    # 1. Indicators: RSI is our 'Fear/Greed' Compass
    bars['RSI'] = ta.rsi(bars['close'], length=14)

    balance = start_balance
    btc_amount = 0
    in_trade = False

    for i in range(1, len(bars)):
        row = bars.iloc[i]
        prev_row = bars.iloc[i-1]

        # ENTRY: Only when the market is screaming (RSI < 35)
        # This is 'Buying the Blood'
        if not in_trade and prev_row['RSI'] < 35:
            btc_amount = balance / row['open']
            balance = 0
            in_trade = True
            print(f"🟢 Sovereign Entry at ${row['open']:,.2f} (Fear Buy)")

        # EXIT: Only when the market is euphoric (RSI > 70)
        # This is 'Harvesting the Greed'
        if in_trade:
            if prev_row['RSI'] > 70:
                balance = btc_amount * row['open']
                btc_amount = 0
                in_trade = False
                print(f"💰 Sovereign Harvest at ${row['open']:,.2f} (Greed Sell)")

    # Final tally (including current value if still in a trade)
    final_val = balance + (btc_amount * bars.iloc[-1]['close'])
    roi = ((final_val - start_balance) / start_balance) * 100
    print(f"\n--- 🏛️ BITCOIN SOVEREIGN FINAL REPORT ---")
    print(f"Final Value: ${final_val:,.2f} | Total ROI: {roi:.2f}%")

if __name__ == "__main__":
    run_bitcoin_sovereign_audit()