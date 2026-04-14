import requests
import json
import time
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. Firebase Initializing ---
try:
    # GitHub Action ထဲမှာဆိုရင် firebase_key.json ရှိနေဖို့လိုပါတယ်
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firestore Connected!")
except Exception as e:
    print(f"❌ Firebase Init Error: {e}")
    db = None

BASE_LIST = "https://lotto.api.rayriffy.com/list/"
BASE_DETAIL = "https://lotto.api.rayriffy.com/lotto/"

def push_to_firestore(all_data):
    """ Firestore ထဲသို့ ဒေတာများကို အစ်ကိုလိုချင်တဲ့ structure အတိုင်း ပို့ပေးခြင်း """
    if not db:
        print("⚠️ Skipping Firestore: DB not initialized.")
        return

    for entry in all_data:
        date_id = entry.get("date")
        if not date_id:
            continue
        
        doc_ref = db.collection("lotto_results").document(date_id)
        
        # Prizes format ကို အစ်ကိုတောင်းထားတဲ့အတိုင်း ပြန်ပြင်မယ်
        formatted_prizes = []
        # အစ်ကိုပြထားတဲ့ raw data ထဲမှာ prizes က array ဖြစ်နေလို့ loop ပတ်ပါတယ်
        for p in entry.get("prizes", []):
            formatted_prizes.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "number": p.get("number")
            })

        try:
            doc_ref.set({
                "date": date_id,
                "prizes": formatted_prizes,
                "updated_at": firestore.SERVER_TIMESTAMP
            })
            print(f"🚀 Firestore Sync: {date_id}")
        except Exception as e:
            print(f"❌ Firestore Error for {date_id}: {e}")

def fetch_and_sync():
    all_raw_data = []
    
    # Page 1 မှ 5 အထိ (အကုန်လိုချင်ရင် range ကို တိုးနိုင်ပါတယ်)
    for page in range(1, 6):
        print(f"📡 Fetching page {page}...")
        try:
            res = requests.get(f"{BASE_LIST}{page}", timeout=20)
            if res.status_code != 200:
                print(f"❌ Page {page} Error: {res.status_code}")
                continue
            
            list_data = res.json()
            items = list_data.get("response", [])
            
            if not items:
                print(f"⏹️ No more items found.")
                break

            for item in items:
                lotto_id = item["id"]
                try:
                    detail_res = requests.get(f"{BASE_DETAIL}{lotto_id}", timeout=20)
                    if detail_res.status_code == 200:
                        raw_content = detail_res.json().get("response", {})
                        if raw_content:
                            all_raw_data.append(raw_content)
                            print(f"🔍 Captured: {raw_content.get('date')}")
                    
                    time.sleep(0.4) # API Rate limit အတွက် ခဏနားတာပါ
                    
                except Exception as e:
                    print(f"⚠️ Error fetching detail {lotto_id}: {e}")
                    continue

        except Exception as e:
            print(f"⚠️ Error fetching page {page}: {e}")
            continue

    # --- ၂ ခုလုံးအတွက် လုပ်ဆောင်ချက် ---
    if all_raw_data:
        # ၁။ JSON File အဖြစ် သိမ်းမယ် (နဂို logic)
        with open("lotto.json", "w", encoding="utf-8") as f:
            json.dump(all_raw_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Local JSON saved: {len(all_raw_data)} dates.")

        # ၂။ Firestore ထဲကို ပို့မယ် (အသစ်ပေါင်းထားတဲ့ logic)
        push_to_firestore(all_raw_data)
    else:
        print("❌ No data captured.")

if __name__ == "__main__":
    print("🚀 Starting Integrated Scraper (JSON + Firestore)...")
    fetch_and_sync()
    print("✨ Process Completed.")
    
