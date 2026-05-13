import requests
import json

url = "https://impl4.taqtics.co/api/v1/external/auth"
payload = {
    "email": "harshit.rajput@taqtics.co",
    "password": "Sahkir12345@"
}

print(f"Testing with 'email' key...")
r = requests.post(url, json=payload)
print(f"Status: {r.status_code}")
print(f"Body: {r.text}")

payload_username = {
    "username": "harshit.rajput@taqtics.co",
    "password": "Sahkir12345@"
}

print(f"\nTesting with 'username' key...")
r = requests.post(url, json=payload_username)
print(f"Status: {r.status_code}")
print(f"Body: {r.text}")
