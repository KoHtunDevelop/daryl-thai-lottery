import requests
import firebase_admin
from firebase_admin import credentials, firestore
import json

# 1. Firebase Initialize
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase Connected!")
except Exception as e:
    print("❌ Firebase Error:", e)

# 2. Sync Function
def sync_lotto():
    url = "https://raw.githubusercontent.com/KoHtunDevelop/daryl-thai-lottery/refs/heads/main/lotto.json"
    
    try:
        response = requests.get(url)
        data_list = response.json()
        
        print(f"🚀 Found {len(data_list)} dates. Syncing...")

        for entry in data_list:
            # GitHub JSON မှာက 'date' နဲ့ 'results' (သို့) 'prizes' ဘာပါလဲ သေချာကြည့်ရအောင်
            # ဒီမှာ 'date' ကို ID အဖြစ် သုံးမယ်
            draw_date = entry.get('date')
            
            # JSON structure အရ prize list ကို ယူမယ်
            # တကယ်လို့ GitHub ထဲမှာ key name က 'results' ဖြစ်နေရင် အောက်ကအတိုင်း ယူပါမယ်
            prizes_list = entry.get('results', []) 

            if not draw_date:
                continue

            # Firestore collection အမည်ကို 'lotto_data' ဟု ပေးထားပါသည်
            doc_ref = db.collection("lotto_data").document(draw_date)

            # Firestore ထဲ ပို့မယ့် format
            final_data = {
                "date": draw_date,
                "all_results": prizes_list, # Array ထဲမှာ prize နဲ့ ticket တွဲလျက် ပါသွားပါမယ်
                "imported_at": firestore.SERVER_TIMESTAMP
            }

            doc_ref.set(final_data, merge=True)
            print(f"✅ Saved: {draw_date}")

        print("\n🔥 အားလုံးပြီးပါပြီ။ Firestore Console ကို Refresh လုပ်ပြီး 'lotto_data' collection ကို စစ်ကြည့်ပါ။")

    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    sync_lotto()
    
