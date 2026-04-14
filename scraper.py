import requests
import json
import time

BASE_LIST = "https://lotto.api.rayriffy.com/list/"
BASE_DETAIL = "https://lotto.api.rayriffy.com/lotto/"

def fetch_and_save_raw():
    all_raw_data = []
    
    # Page 1 ကနေ 5 အထိ အရင်စမ်းကြည့်ပါ (အကုန်လိုချင်ရင် range ကို တိုးပါ)
    for page in range(1, 6):
        print(f"📡 Fetching page {page}...")
        try:
            # 1. List API ကို ခေါ်တယ်
            res = requests.get(f"{BASE_LIST}{page}", timeout=20)
            if res.status_code != 200:
                print(f"❌ Page {page} Error: {res.status_code}")
                continue
            
            list_data = res.json()
            items = list_data.get("response", [])
            
            if not items:
                print(f"⏹️ No more items found at page {page}")
                break

            for item in items:
                lotto_id = item["id"]
                print(f"🔍 Getting Detail for ID: {lotto_id}")
                
                try:
                    # 2. တစ်ခုချင်းစီရဲ့ Detail ကို ထပ်ခေါ်တယ်
                    detail_res = requests.get(f"{BASE_DETAIL}{lotto_id}", timeout=20)
                    if detail_res.status_code == 200:
                        detail_json = detail_res.json()
                        raw_content = detail_json.get("response", {})
                        
                        # Data ရှိတယ်ဆိုရင် List ထဲ တန်းထည့်မယ်
                        if raw_content:
                            all_raw_data.append(raw_content)
                    
                    # API limit မမိအောင် ခဏနားပေးတာ (Optional)
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"⚠️ Error fetching detail {lotto_id}: {e}")
                    continue

        except Exception as e:
            print(f"⚠️ Error fetching page {page}: {e}")
            continue

    return all_raw_data

if __name__ == "__main__":
    print("🚀 Starting Raw Data Scraper...")
    
    raw_results = fetch_and_save_raw()
    
    print(f"📊 Total raw lotto objects captured: {len(raw_results)}")

    # Data ရှိခဲ့ရင် lotto.json အဖြစ် သိမ်းမယ်
    if len(raw_results) > 0:
        with open("lotto.json", "w", encoding="utf-8") as f:
            json.dump(raw_results, f, ensure_ascii=False, indent=2)
        print("✅ All raw data saved to lotto.json")
    else:
        print("❌ No data captured. Please check API connection.")
        
