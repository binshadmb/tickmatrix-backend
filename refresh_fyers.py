import os
import requests
import hashlib
import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

# ---------------------------------------------------
# READ SECRETS FROM GITHUB
# ---------------------------------------------------
CLIENT_ID       = os.getenv("FYERS_CLIENT_ID")
SECRET_KEY      = os.getenv("FYERS_SECRET_KEY")
REFRESH_TOKEN   = os.getenv("FYERS_REFRESH_TOKEN")
PIN             = os.getenv("FYERS_PIN")
GH_PAT          = os.getenv("GH_PAT")
REPO            = os.getenv("GITHUB_REPOSITORY")

# ---------------------------------------------------
# FYERS V3 TOKEN REFRESH LOGIC
# ---------------------------------------------------
app_id_secret = f"{CLIENT_ID}:{SECRET_KEY}"
appIdHash = hashlib.sha256(app_id_secret.encode("utf-8")).hexdigest()

url = "https://api-t1.fyers.in/api/v3/validate-refresh-token"

payload = {
    "grant_type": "refresh_token",
    "appIdHash": appIdHash,
    "refresh_token": REFRESH_TOKEN,
    "pin": PIN
}

print("🔄 Refreshing access token via Fyers V3...")

res = requests.post(url, json=payload)
data = res.json()
print("Fyers Response:", data)

if data.get("s") != "ok":
    raise Exception("❌ Failed to refresh token. Check PIN / Refresh Token.")

new_access_token = data["access_token"]
print("✅ Access Token Refreshed Successfully")

# ---------------------------------------------------
# GET GITHUB PUBLIC KEY
# ---------------------------------------------------
headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GH_PAT}"
}

key_url = f"https://api.github.com/repos/{REPO}/actions/secrets/public-key"
key_res = requests.get(key_url, headers=headers).json()

public_key = key_res["key"]
key_id = key_res["key_id"]

public_key_obj = serialization.load_pem_public_key(
    base64.b64decode(public_key)
)

encrypted = public_key_obj.encrypt(
    new_access_token.encode(),
    padding.PKCS1v15()
)

encrypted_b64 = base64.b64encode(encrypted).decode()

# ---------------------------------------------------
# UPDATE FYERS_ACCESS_TOKEN SECRET
# ---------------------------------------------------
update_url = f"https://api.github.com/repos/{REPO}/actions/secrets/FYERS_ACCESS_TOKEN"

update_body = {
    "encrypted_value": encrypted_b64,
    "key_id": key_id
}

update_res = requests.put(update_url, headers=headers, json=update_body)

print("GitHub Update Response Code:", update_res.status_code)

if update_res.status_code in [200, 201]:
    print("🎉 SUCCESS: FYERS_ACCESS_TOKEN updated inside GitHub.")
else:
    print("❌ Failed to update FYERS_ACCESS_TOKEN:", update_res.text)
    raise SystemExit
