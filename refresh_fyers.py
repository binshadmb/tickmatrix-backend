import os
import json
import time
import hashlib
import requests
from dotenv import load_dotenv

# -----------------------------------------------------
# LOAD SECRETS FROM .env
# -----------------------------------------------------
load_dotenv()

CLIENT_ID = os.getenv("FYERS_CLIENT_ID")
SECRET_KEY = os.getenv("FYERS_SECRET_KEY")
PIN = os.getenv("FYERS_PIN")
REFRESH_TOKEN = os.getenv("FYERS_REFRESH_TOKEN")

TOKEN_FILE = "fyers_access.json"

# -----------------------------------------------------
# GENERATE appIdHash (WITH COLON)
# -----------------------------------------------------
raw = f"{CLIENT_ID}:{SECRET_KEY}"
appIdHash = hashlib.sha256(raw.encode("utf-8")).hexdigest()

REFRESH_URL = "https://api-t1.fyers.in/api/v3/validate-refresh-token"


def save_access_token(token: str):
    data = {
        "access_token": token,
        "timestamp": int(time.time())
    }
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_access_token() -> str | None:
    if not os.path.exists(TOKEN_FILE):
        return None

    with open(TOKEN_FILE, "r") as f:
        data = json.load(f)
        return data.get("access_token")


def refresh_access_token() -> str:
    payload = {
        "grant_type": "refresh_token",
        "appIdHash": appIdHash,
        "refresh_token": REFRESH_TOKEN,
        "pin": PIN
    }

    response = requests.post(REFRESH_URL, json=payload)
    data = response.json()

    if data.get("s") != "ok":
        raise Exception(f"FYERS refresh failed: {data}")

    new_token = data["access_token"]
    save_access_token(new_token)
    return new_token


def get_access_token() -> str:
    token = load_access_token()
    if token:
        return token

    return refresh_access_token()


if __name__ == "__main__":
    print("🔄 Fetching Valid FYERS Access Token...")
    token = get_access_token()
    print("\n✔ YOUR ACCESS TOKEN:\n")
    print(token)
