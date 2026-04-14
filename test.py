import requests
from datetime import datetime

BASE_LIST = "https://lotto.api.rayriffy.com/list/"
BASE_DETAIL = "https://lotto.api.rayriffy.com/lotto/"

def format_date(date_str):
    # example: "2026-03-01" → "01-Mar-2026"
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%d-%b-%Y")

def transform_lotto_data(raw):
    result = []
    date = format_date(raw["date"])

    prizes = raw["prizes"]

    # 1️⃣ First Prize
    if "first" in prizes:
        result.append({
            "date": date,
            "ticket_no": prizes["first"],
            "prize_name": "First Prize"
        })

    # 2️⃣ Running Numbers (front/back 3 digits)
    if "runningNumbers" in prizes:
        for num in prizes["runningNumbers"]["frontThree"]:
            result.append({
                "date": date,
                "ticket_no": num,
                "prize_name": "Front 3 digits"
            })

        for num in prizes["runningNumbers"]["backThree"]:
            result.append({
                "date": date,
                "ticket_no": num,
                "prize_name": "Back 3 digits"
            })

    # 3️⃣ 2 digits
    if "lastTwo" in prizes:
        result.append({
            "date": date,
            "ticket_no": prizes["lastTwo"],
            "prize_name": "Last 2 digits"
        })

    # 4️⃣ Other prizes (second, third, etc.)
    if "second" in prizes:
        for num in prizes["second"]:
            result.append({
                "date": date,
                "ticket_no": num,
                "prize_name": "Second Prize"
            })

    if "third" in prizes:
        for num in prizes["third"]:
            result.append({
                "date": date,
                "ticket_no": num,
                "prize_name": "Third Prize"
            })

    if "fourth" in prizes:
        for num in prizes["fourth"]:
            result.append({
                "date": date,
                "ticket_no": num,
                "prize_name": "Fourth Prize"
            })

    if "fifth" in prizes:
        for num in prizes["fifth"]:
            result.append({
                "date": date,
                "ticket_no": num,
                "prize_name": "Fifth Prize"
            })

    return result


def fetch_all_data():
    all_results = []

    for page in range(1, 50):  # adjust if needed
        print(f"Fetching page {page}...")

        res = requests.get(f"{BASE_LIST}{page}")
        data = res.json()

        if not data["response"]:
            break

        for item in data["response"]:
            lotto_id = item["id"]

            detail = requests.get(f"{BASE_DETAIL}{lotto_id}").json()
            raw = detail["response"]

            transformed = transform_lotto_data(raw)
            all_results.extend(transformed)

    return all_results


if __name__ == "__main__":
    data = fetch_all_data()

    print(f"Total records: {len(data)}")

    # preview first 10
    for d in data[:10]:
        print(d)
