import os
from dotenv import load_dotenv
from supabase import create_client

# 1. LOAD CREDENTIALS
load_dotenv()

url = os.getenv("SUPABASE_URL")
# This MUST be the service_role_key to bypass RLS
key = os.getenv("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("❌ ERROR: Missing credentials in .env file! Check your variable names.")
    exit()

supabase = create_client(url, key)

def run_debug_test():
    target_uuid = "981ef817-e186-4b25-b94c-a83255ec9a3a"
    
    try:
        print(f"🛰️  Attempting to update HEIST Vault row: {target_uuid}...")
        
        # Testing update on the standardized_dna_tags column
        response = supabase.table("vault").update({
            "standardized_dna_tags": ["debug_test_success"]
        }).eq("id", target_uuid).execute()
        
        print("✅ SUCCESS! The database accepted the update.")
        print("Response Details:", response)

    except Exception as e:
        print("\n❌ CRITICAL ERROR DETECTED:")
        print(f"Message: {e}")
        
        # Specific advice based on common Supabase blockers
        if "403" in str(e):
            print("\n💡 ARCHITECT NOTE: This is a 403 Forbidden error. Your Row Level Security (RLS) is likely ON and blocking updates. You need to disable RLS for the 'vault' table or add an 'Allow All' policy for the service_role.")
        elif "column" in str(e).lower():
            print("\n💡 ARCHITECT NOTE: The column name 'standardized_dna_tags' might not exist in your table. Double-check the spelling in the Supabase Table Editor.")

if __name__ == "__main__":
    run_debug_test()