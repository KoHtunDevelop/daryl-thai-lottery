import requests
import firebase_admin
from firebase_admin import credentials, firestore
import json

# =========================
# 🔥 Firebase INIT
# =========================
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase initialized & Connected")
except Exception as e:
    print("❌ Firebase init error:", e)

# =========================
# 📥 GitHub JSON Data Fetch
# =========================
JSON_URL = "https://raw.githubusercontent.com/KoHtunDevelop/daryl-thai-lottery/refs/heads/main/lotto.json"

def sync_github_to_firestore():
    print("🚀 Fetching data from GitHub...")
    try:
        response = requests.get(JSON_URL)
        if response.status_code != 200:
            print("❌ Failed to fetch JSON")
            return

        lotto_list = response.json() # GitHub က data သည် array ဖြစ်သည်
        print(f"📦 Found {len(lotto_list)} records. Starting upload...")

        for entry in lotto_list:
            # Entry တစ်ခုချင်းစီမှာ date နဲ့ results ပါတယ်
            draw_date = entry.get('date') # Eg. 01-Apr-2024
            results = entry.get('results', [])

            if not draw_date:
                continue

            # Firestore Document Reference (Date ကို ID အဖြစ်သုံးခြင်းက ပိုသပ်ရပ်သည်)
            doc_ref = db.collection("lotto_results").document(draw_date)

            # သင်လိုချင်တဲ့ structure အတိုင်း ပြန်စီစဉ်ခြင်း
            # prizes array ထဲမှာ prize name နဲ့ ticket တွေကို object တစ်ခုစီ ထည့်မယ်
            formatted_results = []
            for res in results:
                formatted_results.append({
                    "prize": res.get("prize"),
                    "ticket": res.get("ticket")
                })

            data_to_save = {
                "date": draw_date,
                "all_prizes": formatted_results,
                "source": "github_import"
            }

            # Batch write သုံးရင် ပိုမြန်ပေမယ့် ရိုးရိုး set နဲ့ အရင်စမ်းကြည့်ရအောင်
            doc_ref.set(data_to_save, merge=True)
            print(f"✅ Synced: {draw_date}")

        print("🏁 All data synced successfully!")

    except Exception as e:
        print("❌ Error during sync:", e)

if __name__ == "__main__":
    sync_github_to_firestore()
    
