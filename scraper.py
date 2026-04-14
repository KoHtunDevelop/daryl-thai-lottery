import requests

BASE_LIST = "https://lotto.api.rayriffy.com/list/"
BASE_DETAIL = "https://lotto.api.rayriffy.com/lotto/"

def transform_lotto_data(raw):
    result = []
    date = raw.get("date", "")  # ✅ Thai 그대로

    prizes = raw.get("prizes", {})

    # 1️⃣ First Prize
    if "first" in prizes:
        result.append({
            "date": date,
            "ticket_no": prizes["first"],
            "prize_name": "First Prize"
        })

    # 2️⃣ Running Numbers
    if "runningNumbers" in prizes:
        for num in prizes["runningNumbers"].get("frontThree", []):
            result.append({
                "date": date,
                "ticket_no": num,
                "prize_name": "Front 3 digits"
            })

        for num in prizes["runningNumbers"].get("backThree", []):
            result.append({
                "date": date,
                "ticket_no": num,
                "prize_name": "Back 3 digits"
            })

    # 3️⃣ Last 2 digits
    if "lastTwo" in prizes:
        result.append({
            "date": date,
            "ticket_no": prizes["lastTwo"],
            "prize_name": "Last 2 digits"
        })

    # 4️⃣ Other prizes
    for prize_type in ["second", "third", "fourth", "fifth"]:
        if prize_type in prizes:
            for num in prizes[prize_type]:
                result.append({
                    "date": date,
                    "ticket_no": num,
                    "prize_name": f"{prize_type.capitalize()} Prize"
                })

    return result


def fetch_all_data():
    all_results = []

    for page in range(1, 100):  # adjust if needed
        print(f"Fetching page {page}...")

        res = requests.get(f"{BASE_LIST}{page}")
        data = res.json()

        if not data.get("response"):
            break

        for item in data["response"]:
            lotto_id = item["id"]

            detail_res = requests.get(f"{BASE_DETAIL}{lotto_id}")
            detail = detail_res.json()

            raw = detail.get("response", {})

            transformed = transform_lotto_data(raw)
            all_results.extend(transformed)

    return all_results


if __name__ == "__main__":
    data = fetch_all_data()

    print(f"Total records: {len(data)}")

    # Save to JSON
    import json
    with open("lotto.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ Saved to lotto.json")
