import os
import redis
from dotenv import load_dotenv
from alpaca.data.live import StockDataStream

# Load the vault
load_dotenv()

# Connect to the Redis reflex cache
r = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), decode_responses=True)

# Initialize the Alpaca Websocket
stream = StockDataStream(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'))

async def trade_handler(data):
    # This function triggers the microsecond a trade happens
    log_msg = f"[{data.symbol}] Price: ${data.price:.2f} | Size: {data.size}"
    print(log_msg)

    # Slam the current price into Redis memory
    r.set(f"live_price:{data.symbol}", data.price)

print("Opening dedicated websocket to Alpaca...")
print("Streaming live SPY trades directly to Redis. Press Ctrl+C to terminate.\n")

# Subscribe to live trades for SPY
stream.subscribe_trades(trade_handler, "SPY")

# Ignite the stream
try:
    stream.run()
except KeyboardInterrupt:
    print("\nStream terminated by architect.")