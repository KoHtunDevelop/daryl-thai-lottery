import requests
import json

BASE_LIST = "https://lotto.api.rayriffy.com/list/"
BASE_DETAIL = "https://lotto.api.rayriffy.com/lotto/"

def transform_lotto_data(raw):
    if not isinstance(raw, dict):
        return []

    result = []
    # API ကနေလာတဲ့ date အတိုင်းယူမယ် (ဥပမာ- "1 มีนาคม 2565" သို့မဟုတ် "1 March 2024")
    date_str = raw.get("date", "Unknown Date")
    prizes = raw.get("prizes", {})

    # --- 1. First Prize ---
    if "first" in prizes and prizes["first"]:
        # တစ်ခါတလေ List အနေနဲ့လာတတ်လို့ string/list ခွဲစစ်တာပါ
        val = prizes["first"]
        if isinstance(val, list):
            for v in val:
                result.append({"date": date_str, "ticket no": v, "prize_name": "First Prize"})
        else:
            result.append({"date": date_str, "ticket no": val, "prize_name": "First Prize"})

    # --- 2. Running Numbers (Front 3, Back 3, Last 2) ---
    rn = prizes.get("runningNumbers", {})
    if rn:
        # Front Three
        for num in rn.get("frontThree", []):
            result.append({"date": date_str, "ticket no": num, "prize_name": "Front 3 digits"})
            
        # Back Three
        for num in rn.get("backThree", []):
            result.append({"date": date_str, "ticket no": num, "prize_name": "Back 3 digits"})

        # Last Two
        last_two = rn.get("lastTwo")
        if last_two:
            result.append({"date": date_str, "ticket no": last_two, "prize_name": "Last 2 digits"})

    # --- 3. Other prizes (2nd to 5th) ---
    prize_map = {
        "second": "Second Prize",
        "third": "Third Prize",
        "fourth": "Fourth Prize",
        "fifth": "Fifth Prize",
        "nearbyFirst": "Nearby First Prize"
    }

    for key, display_name in prize_map.items():
        if key in prizes and isinstance(prizes[key], list):
            for num in prizes[key]:
                result.append({
                    "date": date_str,
                    "ticket no": str(num),
                    "prize_name": display_name
                })

    return result

def fetch_all_data():
    all_results = []
    # စမ်းသပ်ဖို့ စာမျက်နှာ ၁ ကနေ ၃ အထိပဲ အရင်ဆွဲကြည့်ပါ
    for page in range(1, 4):
        print(f"📡 Fetching page {page}...")
        try:
            res = requests.get(f"{BASE_LIST}{page}", timeout=15)
            if res.status_code != 200: continue
            data = res.json()
        except: continue

        if not data.get("response"): break

        for item in data["response"]:
            lotto_id = item["id"]
            try:
                detail_res = requests.get(f"{BASE_DETAIL}{lotto_id}", timeout=15)
                if detail_res.status_code != 200: continue
                detail = detail_res.json()
                raw_data = detail.get("response", {})
                
                if raw_data:
                    transformed = transform_lotto_data(raw_data)
                    all_results.extend(transformed)
                    # Debug message
                    print(f"✅ Processed: {raw_data.get('date')} | Found: {len(transformed)} records")
            except:
                continue

    return all_results

if __name__ == "__main__":
    final_data = fetch_all_data()
    print(f"📊 Total individual records captured: {len(final_data)}")

    # Data ရှိမှသာ JSON သိမ်းမယ်
    if len(final_data) > 0:
        with open("lotto.json", "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        print("💾 Saved to lotto.json")
    else:
        print("⚠️ No data found to save.")
                      
