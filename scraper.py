import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://news.sanook.com"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_links():
    links = []

    for page in range(1, 10):  # increase later
        url = f"{BASE_URL}/lotto/archive/page/{page}/"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)

            if "/lotto/" in href and "ตรวจหวย" in text:
                links.append(href)

        print(f"Page {page} -> {len(links)} links")

    return list(set(links))


def parse_detail(url):
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    data = {
        "url": url,
        "title": soup.title.text.strip() if soup.title else ""
    }

    # ✅ หวย results extraction (flexible)
    numbers = []

    for tag in soup.find_all(["h2", "h3", "p", "span"]):
        text = tag.get_text(strip=True)

        if any(keyword in text for keyword in ["รางวัล", "เลข"]):
            numbers.append(text)

    data["results"] = numbers

    return data


def scrape():
    all_data = []
    links = get_links()

    print(f"Total links: {len(links)}")

    for i, link in enumerate(links):
        try:
            data = parse_detail(link)
            all_data.append(data)

            print(f"[{i+1}/{len(links)}] done")
            time.sleep(1)

        except Exception as e:
            print("Error:", e)

    with open("lotto.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print("Saved lotto.json")


if __name__ == "__main__":
    scrape()
