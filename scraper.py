import requests
from bs4 import BeautifulSoup
import json

def scrape_lotto():
    results = []
    # ပထမဆုံး ၅ စာမျက်နှာကို ဆွဲမယ် (လိုသလောက် ပြင်နိုင်ပါတယ်)
    for page in range(1, 6):
        url = f"https://news.sanook.com/lotto/archive/page/{page}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = soup.find_all('article', class_='archive-items')
        for item in articles:
            title = item.find('h3').text.strip()
            link = item.find('a')['href']
            results.append({
                "title": title,
                "url": link
            })
            
    # JSON file အဖြစ်သိမ်းမယ်
    with open('lotto.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    scrape_lotto()
  
