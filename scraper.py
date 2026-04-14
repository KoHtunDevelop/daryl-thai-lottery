import requests
from bs4 import BeautifulSoup
import json

def scrape_lotto():
    results = []

    for page in range(1, 6):
        url = f"https://news.sanook.com/lotto/archive/page/{page}/"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        links = soup.find_all("a", href=True)

        for a in links:
            title = a.get_text(strip=True)
            href = a["href"]

            if "ตรวจหวย" in title:
                results.append({
                    "title": title,
                    "url": href
                })

        print(f"Page {page} done, total: {len(results)}")

    with open("lotto.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("Done")

if __name__ == "__main__":
    scrape_lotto()
