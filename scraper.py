import requests
import json

BASE_LIST = "https://lotto.api.rayriffy.com/list/"
BASE_DETAIL = "https://lotto.api.rayriffy.com/lotto/"

def transform_lotto_data(raw):
    if not isinstance(raw, dict):
        return []

    result = []
    # ရက်စွဲကို အစ်ကိုပြထားတဲ့ format အတိုင်း (ဥပမာ: March-01-2024) ပြောင်းလဲနိုင်ရန်
    # raw["date"] က "1 March 2024" format နဲ့လာတတ်လို့ အဆင်ပြေအောင် ထားပေးထားပါတယ်
    date_str = raw.get("date", "")

    prizes = raw.get("prizes", {})

    # 1. First Prize (ဒါက String တစ်ခုတည်းလာတာပါ)
    if "first" in prizes:
        result.append({
            "date": date_str,
            "ticket no": prizes["first"],
            "prize_name": "First Prize"
        })

    # 2. Running Numbers (Front 3, Back 3, Last 2)
    if "runningNumbers" in prizes:
        rn = prizes["runningNumbers"]
        
        # Front Three
        for num in rn.get("frontThree", []):
            result.append({
                "date": date_str,
                "ticket no": num,
                "prize_name": "Front 3 digits"
            })
            
        # Back Three
        for num in rn.get("backThree", []):
            result.append({
                "date": date_str,
                "ticket no": num,
                "prize_name": "Back 3 digits"
            })

        # Last Two (ဒါက String တစ်ခုတည်းလာတတ်ပါတယ်)
        if rn.get("lastTwo"):
            result.append({
                "date": date_str,
                "ticket no": rn["lastTwo"],
                "prize_name": "Last 2 digits"
            })

    # 3. Other prizes (2nd to 5th) - list အလိုက်လာတာကို တစ်ခုချင်းစီ ခွဲထုတ်မယ်
    prize_map = {
        "second": "Second Prize",
        "third": "Third Prize",
        "fourth": "Fourth Prize",
        "fifth": "Fifth Prize",
        "nearbyFirst": "Nearby First Prize"
    }

    for key, display_name in prize_map.items():
        if key in prizes:
            for num in prizes[key]:
                result.append({
                    "date": date_str,
                    "ticket no": num,
                    "prize_name": display_name
                })

    return result


def fetch_all_data():
    all_results = []

    # စမ်းသပ်ရန် စာမျက်နှာ ၅ ခုလောက်ပဲ အရင်ထည့်ထားပါတယ်၊ အကုန်လိုချင်ရင် range(1, 100) ပြန်ပြောင်းပါ
    for page in range(1, 6):
        print(f"Fetching page {page}...")

        try:
            res = requests.get(f"{BASE_LIST}{page}", timeout=15)
            if res.status_code != 200:
                continue
            data = res.json()
        except Exception as e:
            print(f"❌ Error fetching page {page}: {e}")
            continue

        if not data.get("response"):
            break

        for item in data["response"]:
            lotto_id = item["id"]

            try:
                detail_res = requests.get(f"{BASE_DETAIL}{lotto_id}", timeout=15)
                if detail_res.status_code != 200:
                    continue
                detail = detail_res.json()
            except Exception as e:
                print(f"❌ Error detail {lotto_id}: {e}")
                continue

            raw_data = detail.get("response", {})
            if raw_data:
                transformed = transform_lotto_data(raw_data)
                all_results.extend(transformed)
                print(f"✅ Processed: {raw_data.get('date')}")

    return all_results


if __name__ == "__main__":
    final_data = fetch_all_data()

    print(f"Total individual records: {len(final_data)}")

    # JSON သိမ်းဆည်းခြင်း
    with open("lotto.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print("✅ Successfully saved to lotto.json in flat structure.")
        
