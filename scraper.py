import re
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore
import time

# ✅ Firebase init
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

BASE_URL = "https://news.sanook.com"


def parse_detail(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    data = {}

    # ✅ Extract date
    title = soup.title.text
    date_match = re.search(r"(\d{1,2})\s(.+?)\s(\d{4})", title)

    if date_match:
        day = date_match.group(1)
        month_th = date_match.group(2)
        year_th = date_match.group(3)

        months = {
            "มกราคม": "Jan",
            "กุมภาพันธ์": "Feb",
            "มีนาคม": "Mar",
            "เมษายน": "Apr",
            "พฤษภาคม": "May",
            "มิถุนายน": "Jun",
            "กรกฎาคม": "Jul",
            "สิงหาคม": "Aug",
            "กันยายน": "Sep",
            "ตุลาคม": "Oct",
            "พฤศจิกายน": "Nov",
            "ธันวาคม": "Dec"
        }

        year = int(year_th) - 543
        month = months.get(month_th, "UNK")

        data["date"] = f"{int(day):02d}-{month}-{year}"

    # ✅ Extract prizes
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

                prizes[prize_name] = nums

    data["prizes"] = prizes
    data["url"] = url

    return data


def get_links():
    links = []

    for page in range(1, 5):
        url = f"{BASE_URL}/lotto/archive/page/{page}/"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)

            if "/lotto/check/" in href and "ตรวจหวย" in text:
                links.append(href)

    return list(set(links))


def upload_to_firestore(data):
    date = data.get("date")

    if not date:
        return

    db.collection("lotto").document(date).set(data)
    print(f"Uploaded: {date}")


def main():
    links = get_links()
    print(f"Total links: {len(links)}")

    for link in links:
        try:
            data = parse_detail(link)
            upload_to_firestore(data)
            time.sleep(1)
        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
