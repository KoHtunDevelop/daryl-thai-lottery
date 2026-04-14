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
    print("🔥 Checking firebase_key.json:", os.path.exists("firebase_key.json"))

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
    db.collection("test").document("ping").set({"status": "ok"})
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
def parse_date(text):
    match = re.search(r"(\d{1,2})\s(.+?)\s(\d{4})", text)

    if not match:
        print("❌ Date parse fail:", text)
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
        print("❌ Month fail:", month_th)
        return None

    year = int(year_th) - 543

    return f"{year}-{month}-{int(day):02d}"


# =========================
# 🧾 Parse Detail Page (FIXED)
# =========================
def parse_detail(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)

        if res.status_code != 200:
            print("❌ HTTP error:", url)
            return None

        soup = BeautifulSoup(res.text, "html.parser")

        # 🔥 FIX: use h1 instead of title (Sanook changed structure)
        h1 = soup.find("h1")
        title_text = h1.get_text(strip=True) if h1 else ""

        date = parse_date(title_text)

        prizes = {}

        # 🔥 FIX: find ALL tables (not just first one)
        tables = soup.find_all("table")

        if not tables:
            print("❌ No tables:", url)
            return None

        for table in tables:
            rows = table.find_all("tr")

            for row in rows:
                cols = row.find_all("td")

                if len(cols) >= 2:
                    prize_name = cols[0].get_text(strip=True)
                    numbers = cols[1].get_text(strip=True)

                    nums = re.findall(r"\d+", numbers)

                    if nums:
                        prizes[prize_name] = nums

        print("📊 DEBUG")
        print("URL:", url)
        print("DATE:", date)
        print("PRIZES:", len(prizes))

        if not date or not prizes:
            print("⚠️ Skip invalid:", url)
            return None

        data = {
            "date": date,
            "prizes": prizes,
            "url": url
        }

        # 🔥 Firestore safe
        data = json.loads(json.dumps(data))

        return data

    except Exception as e:
        print("❌ parse_detail error:", e)
        return None


# =========================
# 🔗 Get Links (FIXED)
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

            # 🔥 FIX: more flexible link detection
            for a in soup.find_all("a", href=True):
                href = a["href"]

                if "/lotto/check/" in href:
                    full_url = href if href.startswith("http") else BASE_URL + href
                    links.append(full_url)

            print(f"📄 Page {page} scanned")

        except Exception as e:
            print("❌ get_links error:", e)

    unique_links = list(set(links))
    print("🔗 Total links:", len(unique_links))

    return unique_links


# =========================
# ☁️ Upload to Firestore (FIXED)
# =========================
def upload_to_firestore(data):
    if not data or "date" not in data:
        print("❌ Invalid data:", data)
        return

    date = data["date"]

    try:
        doc_ref = db.collection("lotto").document(date)

        # 🔥 IMPORTANT: always write (no skip)
        doc_ref.set(data, merge=True)

        print(f"✅ Uploaded: {date}")

    except Exception as e:
        print(f"❌ Firestore error:", e)


# =========================
# 🚀 MAIN
# =========================
def main():
    print("🚀 START SCRAPER")

    links = get_links()

    if not links:
        print("❌ No links found")
        return

    success = 0

    for i, link in enumerate(links):
        print(f"[{i+1}/{len(links)}] {link}")

        data = parse_detail(link)

        if data:
            upload_to_firestore(data)
            success += 1
        else:
            print("⚠️ No data")

        time.sleep(1)

    print("🔥 SUCCESS COUNT:", success)
    print("✅ DONE")


if __name__ == "__main__":
    main()
