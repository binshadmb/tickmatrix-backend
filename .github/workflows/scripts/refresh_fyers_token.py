import os
import json
import boto3
import requests
from datetime import datetime

def refresh_fyers_token():
    url = "https://api.fyers.in/api/v3/refresh-token"

    payload = {
        "grant_type": "refresh_token",
        "client_id": os.environ["FYERS_CLIENT_ID"],
        "refresh_token": os.environ["FYERS_REFRESH_TOKEN"],
        "appIdHash": os.environ["FYERS_APP_ID_HASH"]
    }

    response = requests.post(url, json=payload)
    data = response.json()

    print("Response:", data)

    if "access_token" not in data:
        raise Exception("Failed to refresh token: " + str(data))

    return data["access_token"], data["refresh_token"]

def upload_to_s3(access_token, refresh_token):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
    )

    bucket, key = os.environ["AWS_S3_BUCKET"].split("/", 1)

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

if __name__ == "__main__":
    access_token, refresh_token = refresh_fyers_token()
    upload_to_s3(access_token, refresh_token)
    print("✔ Tokens refreshed & uploaded to S3 successfully!")
