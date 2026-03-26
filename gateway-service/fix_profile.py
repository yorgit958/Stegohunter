from supabase import create_client, Client
from app.core.config import settings
from app.core.supabase_client import service_client

def insert_missing_profile():
    user_id = "b13cfc79-9bdd-4e8d-84c8-730f10f09e22"
    log = []
    log.append(f"Attempting to insert profile for {user_id}...")
    
    try:
        response = service_client.table("profiles").insert({
            "id": user_id,
            "email": "user@example.com",
            "username": "ThreatHunter",
        }).execute()
        
        log.append(f"Successfully inserted profile: {response.data}")
    except Exception as e:
        log.append(f"Error inserting profile: {e}")
        log.append("Attempting update instead...")
        try:
             response = service_client.table("profiles").update({
                 "username": "ThreatHunter"
             }).eq("id", user_id).execute()
             log.append(f"Update response: {response.data}")
        except Exception as e2:
             log.append(f"Update failed: {e2}")
             
    with open('fix_log.txt', 'w') as f:
        f.write('\n'.join(log))

if __name__ == "__main__":
    insert_missing_profile()
