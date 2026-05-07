import os
import time
import google.generativeai as genai
from supabase import create_client

# 1. Configuration
GEMINI_KEY = "AIzaSyA66k6YQLP-7xjkdSpV9wpF7PmTuCoptwc"
SUPABASE_URL = "https://xhsxktsnmrrsxcmouqki.supabase.co"
# CRITICAL: Use the SERVICE_ROLE_KEY to bypass RLS for admin work
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc3hrdHNubXJyc3hjbW91cWtpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3Nzc0NTA3NywiZXhwIjoyMDkzMzIxMDc3fQ.TpECz46tVSkjU443BONnGvK6MBHLPyXLcacIA80ZG4A"

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# 2. The Strict Category List
VALID_CATEGORIES = [
    "shirt", "pant", "shorts", "footwear", "jewelry", 
    "co-ords", "suits", "jackets/coats", "t-shirt", "sweatshirt/hoodie"
]

def classify_items():
    # Fetch items where category is still empty
    response = supabase.table("vault").select("id, auditor_note").is_("item_category", "null").execute()
    items = response.data

    print(f"🚀 Processing {len(items)} items...")

    for item in items:
        note = item.get('auditor_note', '')
        
        prompt = f"""
        Strictly classify this fashion item based on the note provided. 
        You MUST return ONLY one of the following lowercase strings:
        [{', '.join(VALID_CATEGORIES)}]

        Auditor Note: "{note}"
        """

        try:
            # Generate classification
            result = model.generate_content(prompt)
            prediction = result.text.strip().lower()

            # Validation check
            if prediction in VALID_CATEGORIES:
                supabase.table("vault").update({"item_category": prediction}).eq("id", item['id']).execute()
                print(f"✅ ID {item['id']}: Classified as [{prediction}]")
            else:
                print(f"⚠️ ID {item['id']}: Gemini returned invalid category '{prediction}'")
            
            # Rate limiting (adjust based on your tier)
            time.sleep(1) 

        except Exception as e:
            print(f"❌ Error on ID {item['id']}: {str(e)}")

if __name__ == "__main__":
    classify_items()