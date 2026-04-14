import re
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore
import time

# =========================
# 🔥 Firebase INIT (SAFE)
# =========================
try:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
    print("✅ Firebase initialized")
except Exception as e:
    print("❌ Firebase init error:", e)

db = firestore.client()

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

    year = int(year_th) - 543
    month = months.get(month_th)

    if not month:
        return None

    return f"{year}-{month}-{int(day):02d}"  # ISO format


# =========================
# 🧾 Parse Detail Page
# =========================
def parse_detail(url):
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    title = soup.title.text if soup.title else ""
    date = parse_date(title)

    prizes = {}

    table = soup.find("table")

    if table:
        rows = table.find_all("tr")

        for row in rows:
            cols = row.find_all("td")

            if len(cols) >= 2:
                prize_name = cols[0].get_text(strip=True)
                numbers = cols[1].get_text(strip=True)

                nums = re.findall(r"\d+", numbers)

                if nums:
                    prizes[prize_name] = nums

    if not date or not prizes:
        print(f"⚠️ Skip invalid data: {url}")
        return None

    return {
        "date": date,
        "prizes": prizes,
        "url": url
    }


# =========================
# 🔗 Get Links
# =========================
def get_links():
    links = []

    for page in range(1, 5):
        url = f"{BASE_URL}/lotto/archive/page/{page}/"
        res = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)

            if "/lotto/check/" in href and "ตรวจหวย" in text:
                links.append(href)

        print(f"Page {page} scanned")

    return list(set(links))


# =========================
# ☁️ Upload to Firestore
# =========================
def upload_to_firestore(data):
    date = data["date"]

    try:
        doc_ref = db.collection("lotto").document(date)

        # 🔥 check duplicate
        if doc_ref.get().exists:
            print(f"⏩ Skip duplicate: {date}")
            return

        doc_ref.set(data)

        print(f"✅ Uploaded: {date}")

    except Exception as e:
        print(f"❌ Firestore error ({date}):", e)


# =========================
# 🚀 MAIN
# =========================
def main():
    print("🚀 START SCRAPER")

    links = get_links()
    print(f"🔗 Total links: {len(links)}")

    for i, link in enumerate(links):
        try:
            print(f"[{i+1}] Processing: {link}")

            data = parse_detail(link)

            if data:
                upload_to_firestore(data)

            time.sleep(1)

        except Exception as e:
            print("❌ Error:", e)

    print("✅ DONE")


if __name__ == "__main__":
    main()
