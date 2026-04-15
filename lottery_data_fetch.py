import requests
import json
import time
import firebase_admin
from firebase_admin import credentials, firestore

try:
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
    if not db:
        print("⚠️ Skipping Firestore: DB not initialized.")
        return

    print(f"🔄 Syncing {len(all_data)} dates to Firestore. Please wait...")
    batch = db.batch()
    count = 0
    total_synced = 0

    for entry in all_data:
        date_id = entry.get("date")
        if not date_id:
            continue
        
        doc_ref = db.collection("lottery_data_update").document(date_id)
        
        formatted_prizes = []
        for p in entry.get("prizes", []):
            formatted_prizes.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "number": p.get("number")
            })

        batch.set(doc_ref, {
            "date": date_id,
            "prizes": formatted_prizes,
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        
        count += 1
        total_synced += 1

        if count >= 400:
            batch.commit()
            print(f"🚀 Batched {total_synced} records...")
            batch = db.batch()
            count = 0
            time.sleep(1)

    if count > 0:
        batch.commit()
        print(f"🚀 Final batch committed. Total: {total_synced}")

def fetch_and_sync():
    all_raw_data = []
    
    for page in range(1, 101):
        print(f"📡 Fetching page {page}...")
        try:
            res = requests.get(f"{BASE_LIST}{page}", timeout=25)
            if res.status_code != 200:
                print(f"⏹️ No more pages or API error at page {page}.")
                break
            
            list_data = res.json()
            items = list_data.get("response", [])
            
            if not items:
                print(f"⏹️ End of data at page {page}.")
                break

            for item in items:
                lotto_id = item["id"]
                try:
                    detail_res = requests.get(f"{BASE_DETAIL}{lotto_id}", timeout=25)
                    if detail_res.status_code == 200:
                        raw_content = detail_res.json().get("response", {})
                        if raw_content:
                            all_raw_data.append(raw_content)
                            print(f"🔍 Captured: {raw_content.get('date')}")
                    
                    time.sleep(0.2) 
                    
                except Exception as e:
                    print(f"⚠️ Detail error {lotto_id}: {e}")
                    continue

        except Exception as e:
            print(f"⚠️ List error at page {page}: {e}")
            break

    if all_raw_data:
        with open("lottery_data_update.json", "w", encoding="utf-8") as f:
            json.dump(all_raw_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Local JSON saved: {len(all_raw_data)} records.")

        push_to_firestore(all_raw_data)
    else:
        print("❌ No data was captured. Please check connection or API.")

if __name__ == "__main__":
    start_time = time.time()
    print("🚀 Starting Integrated Scraper...")
    fetch_and_sync()
    end_time = time.time()
    duration = (end_time - start_time) / 60
    print(f"✨ Process Completed in {duration:.2f} minutes.")
          
