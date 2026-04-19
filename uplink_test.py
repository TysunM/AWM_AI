import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

# Load the vault
load_dotenv()

print("Initiating Alpaca Exchange Uplink...\n")

try:
    # Initialize the client
    trading_client = TradingClient(
        api_key=os.getenv('ALPACA_API_KEY'),
        secret_key=os.getenv('ALPACA_SECRET_KEY'),
        paper=True
    )

    # Request account state
    account = trading_client.get_account()

    print("✅ ALPACA: Connection Established.")
    print(f"   Account Status: {account.status}")
    print(f"   Buying Power: ${float(account.buying_power):,.2f}")
    print(f"   Cash Value: ${float(account.cash):,.2f}")

except Exception as e:
    print(f"❌ ALPACA ERROR: {e}")
    print("Check your API keys and ensure you are using Paper Trading credentials.")

print("\nUplink Complete.")