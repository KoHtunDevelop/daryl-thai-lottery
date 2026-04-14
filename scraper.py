import re
from bs4 import BeautifulSoup
import requests

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

        # Thai → English month map
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

    # ✅ Extract prize table
    prizes = {}

    table = soup.find("table")
    if table:
        rows = table.find_all("tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                prize_name = cols[0].get_text(strip=True)
                numbers = cols[1].get_text(strip=True)

                # clean numbers
                nums = re.findall(r"\d+", numbers)

                prizes[prize_name] = nums

    data["prizes"] = prizes
    data["url"] = url

    return data
