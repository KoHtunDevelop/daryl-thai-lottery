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
    print("✅ Firebase Connected!")

except Exception as e:
    print("❌ Firebase Error:", e)


# =========================
# 🔄 SYNC FUNCTION
# =========================
def sync_lotto():
    url = "https://raw.githubusercontent.com/KoHtunDevelop/daryl-thai-lottery/main/lotto.json"

    try:
        print("🌐 Fetching JSON...")

        response = requests.get(url, timeout=15)

        print("📡 Status Code:", response.status_code)

        if response.status_code != 200:
            print("❌ Failed to fetch JSON")
            return

        try:
            data_list = response.json()
        except Exception as e:
            print("❌ JSON decode error:", e)
            return

        if not data_list:
            print("❌ JSON EMPTY")
            return

        print(f"🚀 Found {len(data_list)} records")

        success = 0

        for entry in data_list:
            draw_date = entry.get("date")

            # 🔥 support both formats
            prizes = entry.get("prizes") or entry.get("results")

            if not draw_date or not prizes:
                print("⚠️ Skip invalid entry:", entry)
                continue

            doc_ref = db.collection("lotto_data").document(draw_date)

            final_data = {
                "date": draw_date,
                "results": prizes,
                "imported_at": firestore.SERVER_TIMESTAMP
            }

            doc_ref.set(final_data, merge=True)

            print(f"✅ Saved: {draw_date}")
            success += 1

        print(f"\n🔥 TOTAL SAVED: {success}")

    except Exception as e:
        print("❌ Error:", e)


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    sync_lotto()
