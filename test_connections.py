import os
import redis
import psycopg2
from dotenv import load_dotenv

# Load the secure credentials from your .env file
load_dotenv()

print("Initiating State Engine Diagnostics...\n")

# --- 1. Test the Redis Cache ---
try:
    r = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), decode_responses=True)
    r.ping()
    print("✅ REDIS: Connected. Reflex cache is online.")
except Exception as e:
    print(f"❌ REDIS ERROR: {e}")

# --- 2. Test the Postgres Vault ---
try:
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print(f"✅ POSTGRES: Connected. Memory vault is online. ({db_version[0][:23]}...)")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ POSTGRES ERROR: {e}")

print("\nDiagnostics Complete.")