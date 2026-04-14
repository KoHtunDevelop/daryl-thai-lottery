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
    # စမ်းသပ်ဖို့ Page 1 တစ်ခုတည်းအရင်ယူကြည့်မယ်
    for page in range(1, 2):
        url = f"{BASE_URL}/lotto/archive/page/{page}/"
        try:
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            # a tag အားလုံးထဲက link တွေကို စစ်ထုတ်မယ်
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/lotto/check/" in href:
                    if href.startswith("/"):
                        links.append(BASE_URL + href)
                    else:
                        links.append(href)
        except Exception as e:
            print(f"Error fetching links: {e}")
    
    unique_links = list(set(links))
    print(f"Found {len(unique_links)} unique links.")
    return unique_links

def parse_detail(url):
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # ရက်စွဲကို ယူမယ် (ဥပမာ: 1 มีนาคม 2567)
        title_text = soup.find("title").text if soup.title else ""
        date_match = re.search(r"(\d+\s+\w+\s+\d+)", title_text)
        formatted_date = date_match.group(1) if date_match else "Unknown Date"

        prizes_data = []

        # Sanook ရဲ့ structural class များကို ဆွဲထုတ်ခြင်း
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
                if ticket_no and ticket_no.isdigit():
                    prizes_data.append({
                        "date": formatted_date,
                        "ticket_no": ticket_no,
                        "prize_name": section["name"]
                    })

        # တခြားဆုများ (2nd to 5th)
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
                if ticket_no and ticket_no.isdigit():
                    prizes_data.append({
                        "date": formatted_date,
                        "ticket_no": ticket_no,
                        "prize_name": name
                    })

        return prizes_data
    except Exception as e:
        print(f"Error parsing {url}: {e}")
        return []

def scrape():
    all_results = []
    links = get_links()
    
    if not links:
        print("No links found. Script stopping.")
        return

    for i, link in enumerate(links):
        print(f"[{i+1}/{len(links)}] Scraping: {link}")
        data = parse_detail(link)
        if data:
            all_results.extend(data)
        time.sleep(1) # Block မဖြစ်အောင် ၁ စက္ကန့်နားမယ်

    if all_results:
        with open("lotto.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"Success! {len(all_results)} entries saved to lotto.json")
    else:
        print("No data collected.")

if __name__ == "__main__":
    scrape()
        
