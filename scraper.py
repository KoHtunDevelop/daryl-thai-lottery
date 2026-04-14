import requests
from bs4 import BeautifulSoup
import json
import time
import re

BASE_URL = "https://news.sanook.com"

headers = {
    "User-Agent": "Mozilla/5.0"
}


def get_links():
    links = []

    for page in range(1, 5):
        url = f"{BASE_URL}/lotto/archive/page/{page}/"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)

            if "/lotto/" in href and "ตรวจหวย" in text:
                links.append(href)

    return list(set(links))


def clean_number(text):
    return re.findall(r"\d+", text)


def extract_date(soup):
    title = soup.find("h1")
    if title:
        text = title.get_text()
        match = re.search(r"([A-Za-z]+ \d{1,2}, \d{4})", text)
        if match:
            return match.group(1).replace(" ", "-").replace(",", "")
    return ""


def parse_detail(url):
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    date = extract_date(soup)

    results = []

    # 🔴 First Prize
    first = soup.find("h2")
    if first:
        nums = clean_number(first.get_text())
        if nums:
            results.append({
                "date": date,
                "ticket_no": nums[0],
                "prize_name": "First Prize"
            })

    # 🔴 3 digits (หน้า 3 ตัว)
    for tag in soup.find_all(string=re.compile("3 ตัวหน้า")):
        parent = tag.find_parent()
        nums = clean_number(parent.get_text())
        for n in nums:
            results.append({
                "date": date,
                "ticket_no": n,
                "prize_name": "Front 3 digits"
            })

    # 🔴 Last 3 digits
    for tag in soup.find_all(string=re.compile("3 ตัวหลัง")):
        parent = tag.find_parent()
        nums = clean_number(parent.get_text())
        for n in nums:
            results.append({
                "date": date,
                "ticket_no": n,
                "prize_name": "Last 3 digits"
            })

    # 🔴 Last 2 digits
    for tag in soup.find_all(string=re.compile("2 ตัว")):
        parent = tag.find_parent()
        nums = clean_number(parent.get_text())
        for n in nums:
            results.append({
                "date": date,
                "ticket_no": n,
                "prize_name": "Last 2 digits"
            })

    # 🔴 Consolation Prize
    for tag in soup.find_all(string=re.compile("ข้างเคียง")):
        parent = tag.find_parent()
        nums = clean_number(parent.get_text())
        for n in nums:
            results.append({
                "date": date,
                "ticket_no": n,
                "prize_name": "Consolation Prize"
            })

    return results


def scrape():
    all_results = []
    links = get_links()

    print(f"Total links: {len(links)}")

    for i, link in enumerate(links):
        try:
            data = parse_detail(link)
            all_results.extend(data)

            print(f"[{i+1}/{len(links)}] done")
            time.sleep(1)

        except Exception as e:
            print("Error:", e)

    with open("lotto.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print("Saved lotto.json")


if __name__ == "__main__":
    scrape()
