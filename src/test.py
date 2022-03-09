import requests
import json

keyword_list = ["주식", "윤석열", "이재명", "투자", "원자재", "기술주", "대기업", "상반기", "하반기"]

url = "http://localhost:8000/v1/donga/articles"
num = 1

data_list = []

for keyword in keyword_list:

    for i in range(1, 300):
        try:
            print(num)
            num += 1

            payload = json.dumps({
                "keyword": keyword,
                "page": i
            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            data = json.loads(response.text)['result']
            if len(data) == 0:
                break
            data_list.extend(data)

        except Exception as e:
            print(e)
            continue

with open('./donga_2.json', 'w') as f:
    json.dump({"result": data_list}, f, ensure_ascii=False)
