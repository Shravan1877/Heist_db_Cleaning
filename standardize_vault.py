import os
import time
from dotenv import load_dotenv
from supabase import create_client
import google.generativeai as genai

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

SYSTEM_INSTRUCTION = "Act as a Master Fashion Auditor for HEIST. Output ONLY a comma-separated list of tags."

def process_with_gemini(tags):
    if not tags or tags == "[]": return []
    try:
        response = model.generate_content(f"{SYSTEM_INSTRUCTION}\n\nTags: {tags}")
        return [t.strip() for t in response.text.split(",") if t.strip()]
    except Exception as e:
        print(f"Gemini Error: {e}")
        return None

def main():
    # Only fetch rows where the DNA tags haven't been standardized yet
    print("🚀 Fetching rows needing standardization...")
    response = supabase.table("vault").select("id, dna_tags, aesthetic_tags").is_("standardized_dna_tags", "null").execute()
    rows = response.data

    if not rows:
        print("✅ No empty rows found. Everything is standardized!")
        return

    print(f"💎 {len(rows)} items found. Starting cleanup...")

    for row in rows:
        row_id = row['id']
        new_dna = process_with_gemini(row.get('dna_tags', []))
        new_aes = process_with_gemini(row.get('aesthetic_tags', []))

        if new_dna is not None:
            try:
                # Update both columns
                supabase.table("vault").update({
                    "standardized_dna_tags": new_dna,
                    "standardized_aesthetic_tags": new_aes
                }).eq("id", row_id).execute()
                print(f"✅ Updated ID: {row_id}")
            except Exception as e:
                print(f"❌ Supabase Update Error on ID {row_id}: {e}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()