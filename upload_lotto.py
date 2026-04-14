import requests
import firebase_admin
from firebase_admin import credentials, firestore
import json

# =========================
# 🔥 1. Firebase Initialize
# =========================
def init_firebase():
    try:
        if not firebase_admin._apps:
            # သင့်ဆီမှာရှိတဲ့ firebase_key.json ဖိုင်နာမည် မှန်အောင် စစ်ပါ
            cred = credentials.Certificate("firebase_key.json")
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        print(f"❌ Firebase Connection Error: {e}")
        return None

# =========================
# 📥 2. Fetch & Upload Data
# =========================
def sync_github_to_firestore():
    db = init_firebase()
    if not db:
        return

    # 🔥 အရေးကြီးဆုံးအချက်: Raw Link ဖြစ်ရပါမယ်
    RAW_JSON_URL = "https://raw.githubusercontent.com/KoHtunDevelop/daryl-thai-lottery/main/lotto.json"

    print("🚀 Fetching data from GitHub...")
    try:
        response = requests.get(RAW_JSON_URL)
        if response.status_code != 200:
            print(f"❌ GitHub Link မှားနေသည် (HTTP {response.status_code})")
            return

        lotto_list = response.json()
        print(f"📦 Found {len(lotto_list)} dates. Syncing to Firestore...")

        for entry in lotto_list:
            draw_date = entry.get('date') # "01-Apr-2024"
            results = entry.get('results', []) # Prize array

            if not draw_date:
                continue

            # Firestore Reference
            # 'lotto_data' ဆိုတဲ့ collection ထဲကို date ကို ID လုပ်ပြီး ထည့်မယ်
            doc_ref = db.collection("lotto_data").document(draw_date)

            # Data Structure ပြင်ဆင်ခြင်း
            upload_data = {
                "date": draw_date,
                "prizes": results,  # GitHub ထဲက array အတိုင်း တိုက်ရိုက်သိမ်းမယ်
                "updated_at": firestore.SERVER_TIMESTAMP
            }

            # Firestore ထဲသို့ သိမ်းဆည်းခြင်း
            doc_ref.set(upload_data, merge=True)
            print(f"✅ Synced: {draw_date}")

        print("\n🔥 SUCCESS! Firestore Console ကို Refresh လုပ်ပြီး 'lotto_data' ကို စစ်ကြည့်ပါ။")

    except Exception as e:
        print(f"❌ Error during sync: {e}")

if __name__ == "__main__":
    sync_github_to_firestore()
      
