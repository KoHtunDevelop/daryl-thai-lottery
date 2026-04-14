import requests

base_list = "https://lotto.api.rayriffy.com/list/"
base_detail = "https://lotto.api.rayriffy.com/lotto/"

all_data = []

for page in range(1, 50):  # pages loop
    res = requests.get(f"{base_list}{page}").json()

    for item in res["response"]:
        lotto_id = item["id"]

        detail = requests.get(f"{base_detail}{lotto_id}").json()
        all_data.append(detail["response"])

print(len(all_data))
