import os
import time
import json
from dotenv import load_dotenv
from supabase import create_client, Client
import google.generativeai as genai

# 1. SETUP: Load credentials
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") # Use Service Role for write access
gemini_key = os.getenv("GEMINI_API_KEY")

supabase: Client = create_client(supabase_url, supabase_key)
genai.configure(api_key=gemini_key)
model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

# 2. SYSTEM PROMPT: Define the "Stylist Logic"
SYSTEM_PROMPT = """
You are a Fashion Data Scientist. Convert item tags into a 4D Style Vector: [Old Money, Ivy, Soft Boy, Streetwear].
Rules:
- Output ONLY a JSON array of 4 floats.
- The sum of the 4 numbers must equal EXACTLY 1.0.
- Old Money (OM): Neutral, high-end fabrics, structured but quiet.
- Ivy (IV): Collegiate, heritage, preppy, loafers, blazers.
- Soft Boy (SB): Fluid, pastel, emotional textures, linen, relaxed.
- Streetwear (SW): Boxy, high-GSM cotton, tech-wear, urban utility.

Example: For a "Cashmere Minimalist Sweater", return [0.8, 0.1, 0.1, 0.0]
"""

def get_vector(brand, tags):
    prompt = f"Brand: {brand}. Tags: {tags}. Return the vector."
    try:
        response = model.generate_content([SYSTEM_PROMPT, prompt])
        # Clean the response to ensure it's just the array
        vector_str = response.text.strip().replace("`", "").replace("json", "")
        vector = json.loads(vector_str)
        
        # Validation: Ensure it's 4 elements and sums to ~1
        if len(vector) == 4 and abs(sum(vector) - 1.0) < 0.01:
            return vector
        else:
            print(f"⚠️ Bad Vector math for {brand}: {vector}")
            return None
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return None

def main():
    # 3. FETCH: Get rows where dna_vector is empty
    print("🛰️ Fetching items without vectors...")
    res = supabase.table("vault").select("id, brand_name, standardized_dna_tags").is_("dna_vector", "null").execute()
    items = res.data

    if not items:
        print("✅ All items are already vectorized!")
        return

    print(f"🧪 Processing {len(items)} items...")

    for item in items:
        item_id = item['id']
        brand = item['brand_name']
        tags = item['standardized_dna_tags']

        print(f"🧬 Vectorizing: {brand}...")
        vector = get_vector(brand, tags)

        if vector:
            # 4. UPDATE: Push back to Supabase
            supabase.table("vault").update({"dna_vector": vector}).eq("id", item_id).execute()
            print(f"✅ Saved: {vector}")
        
        # Avoid rate limits
        time.sleep(1)

if __name__ == "__main__":
    main()