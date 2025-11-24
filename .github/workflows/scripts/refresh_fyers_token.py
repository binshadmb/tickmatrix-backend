import os
import json
import hashlib
import boto3
import requests
from datetime import datetime

def update_s3(access_token, refresh_token):
    bucket_key = os.environ["AWS_S3_BUCKET"]
    bucket, key = bucket_key.split("/", 1)

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
    )

    payload = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "updated_at": datetime.utcnow().isoformat()
    }

    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(payload),
        ContentType="application/json"
    )

def update_repo_file(access_token, refresh_token):
    content = f'''
access_token = "{access_token}"
refresh_token = "{refresh_token}"
last_updated = "{datetime.utcnow().isoformat()}"
'''
    with open("fyers_token.py", "w") as f:
        f.write(content)

def refresh_fyers_token():
    appId = os.environ["FYERS_CLIENT_ID"]
    refresh_token = os.environ["FYERS_REFRESH_TOKEN"]
    appIdHash = os.environ["FYERS_APP_ID_HASH"]

    data = {
        "grant_type": "refresh_token",
        "appId": appId,
        "appIdHash": appIdHash,
        "refresh_token": refresh_token
    }

    url = "https://api-t1.fyers.in/api/v3/refresh-token"

    r = requests.post(url, json=data)
    result = r.json()

    if result.get("s") != "ok":
        print("Error refreshing token:", result)
        return

    new_access = result["access_token"]
    new_refresh = result["refresh_token"]

    update_s3(new_access, new_refresh)
    update_repo_file(new_access, new_refresh)

    print("Token refreshed successfully.")

if __name__ == "__main__":
    refresh_fyers_token()
