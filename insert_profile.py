import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv(r"c:\stego-hunter\gateway-service\.env")

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("ERROR: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in .env")
    sys.exit(1)

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
    "Prefer": "return=representation,resolution=merge-duplicates"
}

# Change this to your actual auth.users UUID
user_id = "b13cfc79-9bdd-4e8d-84c8-730f10f09e22"

# Only include columns that exist on the profiles table
data = {
    "id": user_id,
    "username": "nikhils0818",
    "role": "admin",
    "is_active": True
}

try:
    response = requests.post(f"{url}/rest/v1/profiles", headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    if response.status_code in (200, 201):
        print("SUCCESS: Profile inserted/updated.")
    else:
        print(f"FAILED: {response.status_code}")
except Exception as e:
    print(f"Exception: {e}")
