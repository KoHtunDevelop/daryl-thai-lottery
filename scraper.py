import requests
from bs4 import BeautifulSoup
import json
import time
import re

BASE_URL = "https://news.sanook.com"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_links():
    links = []
    # စမ်းသပ်ရန် page 1-2 လောက်ပဲ အရင်ယူကြည့်ပါ (နောက်မှ တိုးလို့ရပါတယ်)
    for page in range(1, 3):
        url = f"{BASE_URL}/lotto/archive/page/{page}/"
        try:
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                text = a.get_text(strip=True)
                if "/lotto/check/" in href and "ตรวจหวย" in text:
                    links.append(href)
        except Exception as e:
            print(f"Error fetching links: {e}")
    return list(set(links))

def parse_detail(url):
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    
    # ရက်စွဲကို Title ထဲကနေ ယူတာ (ဥပမာ: 1 มีนาคม 2567)
    title_text = soup.find("title").text if soup.title else ""
    date_match = re.search(r"(\d+\s+\w+\s+\d+)", title_text)
    formatted_date = date_match.group(1) if date_match else "Unknown Date"

    prizes_data = []

    # Sanook ရဲ့ structural class တွေကို သုံးပြီး ဆွဲထုတ်ခြင်း
    sections = [
        {"name": "First Prize", "class": "lotto__number--p1"},
        {"name": "Front 3 Digits", "class": "lotto__number--p2"},
        {"name": "Last 3 Digits", "class": "lotto__number--p3"},
        {"name": "Last 2 Digits", "class": "lotto__number--p4"}
    ]

    for section in sections:
        tags = soup.find_all("strong", class_=section["class"])
        for tag in tags:
            ticket_no = tag.get_text(strip=True)
            if ticket_no:
                prizes_data.append({
                    "date": formatted_date,
                    "ticket_no": ticket_no,
                    "prize_name": section["name"]
                })

    # တခြားဆုများ (2nd, 3rd, 4th, 5th)
    other_prizes = {
        "Second Prize": "lotto__number--p2nd",
        "Third Prize": "lotto__number--p3rd",
        "Fourth Prize": "lotto__number--p4th",
        "Fifth Prize": "lotto__number--p5th"
    }

    for name, cls in other_prizes.items():
        tags = soup.find_all("span", class_=cls)
        for tag in tags:
            ticket_no = tag.get_text(strip=True)
            if ticket_no:
                prizes_data.append({
                    "date": formatted_date,
                    "ticket_no": ticket_no,
                    "prize_name": name
                })

    return prizes_data

def scrape():
    all_results = []
    links = get_links()
    print(f"Found {len(links)} links. Starting extraction...")

    for i, link in enumerate(links):
        try:
            data = parse_detail(link)
            all_results.extend(data) # Flatten list
            print(f"[{i+1}/{len(links)}] Scraped: {link}")
            time.sleep(1) # Site block မဖြစ်အောင် ခေတ္တနားခြင်း
        except Exception as e:
            print(f"Error on {link}: {e}")

    with open("lotto.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print("Done! Data saved to lotto.json")

if __name__ == "__main__":
    scrape()
    
