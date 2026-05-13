import requests
import json
from datetime import datetime

# 1. Auth first
url_auth = "https://impl4.taqtics.co/api/v1/external/auth"
payload = {
    "email": "harshit.rajput@taqtics.co",
    "password": "Sahkir12345@"
}
r_auth = requests.post(url_auth, json=payload)
token = r_auth.json().get('token')
headers = {"access-token": token}

# 2. Test CSV
url_csv_base = "https://impl4.taqtics.co/api/v1/external/blobs/csvs/monthly"
month = "01-2026"
form_id = "IMPFORM115"

print(f"Fetching CSV link for {form_id} / {month}...")
params = {"formId": form_id, "monthYear": month}
r = requests.get(url_csv_base, headers=headers, params=params)
if r.status_code == 200:
    print(f"Full JSON: {r.json()}")
    blob_url = r.json().get('fileUrl')
    print(f"Blob URL found. Downloading...")
    csv_r = requests.get(blob_url)
    content = csv_r.text
    header = content.strip().splitlines()[0]
    print(f"Header: {header}")
    print(f"Sample Row: {content.strip().splitlines()[1]}")
else:
    print(f"Failed to get blob: {r.status_code} {r.text}")
