import os
import requests
from dotenv import load_dotenv

# Load your environment variables
load_dotenv()

def fire_test_signal():
    topic = os.getenv('NTFY_TOPIC')

    if not topic:
        print("❌ Error: NTFY_TOPIC is missing from your .env file.")
        return

    print(f"Attempting to broadcast to Ntfy topic: {topic}...")

    # The payload
    message = "System Online: The Alchemical Engine is live and listening."

    try:
        response = requests.post(f"https://ntfy.sh/{topic}",
            data=message.encode('utf-8'),
            headers={
                "Title": "Engine Status",
                "Priority": "high",
                "Tags": "ghost,zap"
            })

        if response.status_code == 200:
            print("✅ Signal sent successfully. Check your phone.")
        else:
            print(f"⚠️ Signal failed. Ntfy returned status: {response.status_code}")

    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    fire_test_signal()