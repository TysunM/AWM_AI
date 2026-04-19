# Initialize Clients
data_client = StockHistoricalDataClient(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'))
trade_client = TradingClient(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'))

def get_high_momentum_universe():
    print("\n🔭 SCANNER: Hunting for high-energy assets...")
    assets = trade_client.get_all_assets()
    # Filter for active, tradable NASDAQ stocks
    symbols = [a.symbol for a in assets if a.tradable and a.fractionable and a.exchange == 'NASDAQ']

    # Increase chunk size to find more candidates
    search_chunk = symbols[:500]

    try:
        snapshot_request = StockSnapshotRequest(symbol_or_symbols=search_chunk)
        snapshots = data_client.get_stock_snapshot(snapshot_request)
        momentum_list = []

        for symbol, snapshot in snapshots.items():
            try:
                current_price = snapshot.latest_trade.price
                # If we are in pre-market, use the last known close
                prev_close = snapshot.prev_daily_bar.close if snapshot.prev_daily_bar else current_price

                price_change = ((current_price - prev_close) / prev_close) * 100

                # Widen the filter for Pre-Market (1.0% change or high price)
                if current_price > 5 and (abs(price_change) > 1.0):
                    momentum_list.append((symbol, price_change))
            except Exception:
                continue

        # If momentum search fails, grab a default high-liquidity list
        if not momentum_list:
            print("⚠️ Low momentum detected. Defaulting to High-Liquidity Tech Universe.")
            return ["AAPL", "MSFT", "NVDA", "TSLA", "AMD", "META", "AMZN", "GOOGL", "NFLX", "AVGO"]

        momentum_list.sort(key=lambda x: x[1], reverse=True)
        final_universe = [x[0] for x in momentum_list[:50]]

        print(f"✅ SCANNER COMPLETE: Found {len(final_universe)} momentum candidates.")
        return final_universe

    except Exception as e:
        print(f"❌ SCANNER ERROR: {e}")
        return ["AAPL", "MSFT", "NVDA"]

if __name__ == "__main__":
    get_high_momentum_universe()