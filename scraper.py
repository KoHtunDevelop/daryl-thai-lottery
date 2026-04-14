from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import time

def scrape_lotto():
    driver = webdriver.Chrome()
    results = []

    for page in range(1, 4):
        url = f"https://news.sanook.com/lotto/archive/page/{page}"
        driver.get(url)
        time.sleep(3)

        items = driver.find_elements(By.CSS_SELECTOR, "a[href*='/lotto/']")

        for item in items:
            title = item.text.strip()
            link = item.get_attribute("href")

            if "ตรวจหวย" in title:
                results.append({
                    "title": title,
                    "url": link
                })

        print(f"Page {page} done")

    driver.quit()

    with open("lotto.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

scrape_lotto()
