import re
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore
import time
import json
import os

# =========================
# 🔥 Firebase INIT
# =========================
try:
    print("🔥 Checking firebase_key.json ...", os.path.exists("firebase_key.json"))

    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
    print("✅ Firebase initialized")

except Exception as e:
    print("❌ Firebase init error:", e)

db = firestore.client()

# =========================
# 🧪 TEST FIREBASE WRITE
# =========================
print("🔥 TEST FIREBASE CONNECTION")

try:
    test_ref = db.collection("test").document("ping")
    test_ref.set({"status": "ok"})
    print("✅ Firestore WRITE SUCCESS")
except Exception as e:
    print("❌ Firestore WRITE FAILED:", e)

BASE_URL = "https://news.sanook.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# =========================
# 📅 Parse Date
# =========================
def parse_date(title):
    match = re.search(r"(\d{1,2})\s(.+?)\s(\d{4})", title)

    if not match:
        print("❌ Date regex fail:", title)
        return None

    day = match.group(1)
    month_th = match.group(2)
    year_th = match.group(3)

    months = {
        "มกราคม": "01",
        "กุมภาพันธ์": "02",
        "มีนาคม": "03",
        "เมษายน": "04",
        "พฤษภาคม": "05",
        "มิถุนายน": "06",
        "กรกฎาคม": "07",
        "สิงหาคม": "08",
        "กันยายน": "09",
        "ตุลาคม": "10",
        "พฤศจิกายน": "11",
        "ธันวาคม": "12"
    }

    month = months.get(month_th)

    if not month:
        print("❌ Month parse fail:", month_th)
        return None

    year = int(year_th) - 543

    return f"{year}-{month}-{int(day):02d}"


# =========================
# 🧾 Parse Detail Page
# =========================
def parse_detail(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)

        if res.status_code != 200:
            print(f"❌ HTTP {res.status_code}:", url)
            return None

        soup = BeautifulSoup(res.text, "html.parser")

        title = soup.title.text if soup.title else ""
        date = parse_date(title)

        prizes = {}

        table = soup.find("table")

        if not table:
            print("❌ No table found:", url)
            return None

        rows = table.find_all("tr")

        for row in rows:
            cols = row.find_all("td")

            if len(cols) >= 2:
                prize_name = cols[0].get_text(strip=True)
                numbers = cols[1].get_text(strip=True)

                nums = re.findall(r"\d+", numbers)

                if nums:
                    prizes[prize_name] = nums

        # 🔥 DEBUG
        print("📊 Parsed:", url)
        print("   Date:", date)
        print("   Prizes count:", len(prizes))

        if not date or not prizes:
            print(f"⚠️ Skip invalid data: {url}")
            return None

        data = {
            "date": date,
            "prizes": prizes,
            "url": url
        }

        # 🔥 sanitize for Firestore
        data = json.loads(json.dumps(data))

        return data

    except Exception as e:
        print("❌ parse_detail error:", e)
        return None


# =========================
# 🔗 Get Links
# =========================
def get_links():
    links = []

    for page in range(1, 6):
        url = f"{BASE_URL}/lotto/archive/page/{page}/"

        try:
            res = requests.get(url, headers=HEADERS, timeout=10)

            if res.status_code != 200:
                print("❌ Page error:", url)
                continue

            soup = BeautifulSoup(res.text, "html.parser")

            for a in soup.find_all("a", href=True):
                href = a["href"]
                text = a.get_text(strip=True)

                if "/lotto/check/" in href and "ตรวจหวย" in text:
                    links.append(href)

            print(f"📄 Page {page} scanned")

        except Exception as e:
            print("❌ get_links error:", e)

    unique_links = list(set(links))
    print("🔗 Unique links:", len(unique_links))

    return unique_links


# =========================
# ☁️ Upload to Firestore
# =========================
def upload_to_firestore(data):
    if not data or "date" not in data:
        print("❌ Invalid data:", data)
        return

    date = data["date"]

    try:
        doc_ref = db.collection("lotto").document(date)

        # 🔥 check existing
        doc = doc_ref.get()

        if doc.exists:
            print(f"⏩ Skip duplicate: {date}")
            return

        doc_ref.set(data, merge=True)

        print(f"✅ Uploaded: {date}")

    except Exception as e:
        print(f"❌ Firestore error ({date}):", e)


# =========================
# 🚀 MAIN
# =========================
def main():
    print("🚀 START SCRAPER")

    links = get_links()

    if not links:
        print("❌ No links found — scraper broken")
        return

    success = 0

    for i, link in enumerate(links):
        print(f"[{i+1}/{len(links)}] Processing:", link)

        data = parse_detail(link)

        if data:
            upload_to_firestore(data)
            success += 1
        else:
            print("⚠️ No data extracted")

        time.sleep(1)

    print("🔥 TOTAL SUCCESS:", success)
    print("✅ DONE")


if __name__ == "__main__":
    main()
