import json
import firebase_admin
from firebase_admin import credentials, db

try:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://daryl-a101e-default-rtdb.asia-southeast1.firebasedatabase.app/'
    }, name='prize_app')
    print("✅ RTDB Connected!")
except Exception as e:
    print(f"❌ RTDB Init Error: {e}")

def upload_prize_data():
    prizes = [
        {"name": "First Prize", "count": 1, "reward": 6000000},
        {"name": "The last two digits", "count": 10000, "reward": 2000},
        {"name": "The last three digits", "count": 2000, "reward": 4000},
        {"name": "The first three digits", "count": 2000, "reward": 4000},
        {"name": "Second Prize", "count": 5, "reward": 200000},
        {"name": "Third Prize", "count": 10, "reward": 80000},
        {"name": "Fourth Prize", "count": 50, "reward": 40000},
        {"name": "Fifth Prize", "count": 100, "reward": 20000},
        {"name": "Consolation prize for the first prize", "count": 2, "reward": 100000}
    ]


    with open("prize_data_update.json", "w", encoding="utf-8") as f:
        json.dump(prizes, f, indent=2)

    try:
        ref = db.reference('prize_details', app=firebase_admin.get_app('prize_app'))
        ref.set(prizes)
        print("🚀 Prize Info synced to Realtime Database!")
    except Exception as e:
        print(f"❌ Upload failed: {e}")

if __name__ == "__main__":
    upload_prize_data()
