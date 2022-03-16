import requests
import json
import pickle
from time import sleep

with open("corp_list.pickle", "rb") as fr:
    data = pickle.load(fr)

keyword_list = list(data['corp_name'])
code_list = list(data['stock_code'])

url = "http://localhost:8000/v1/dart/articles"
num = 0
data_list = []
print("key length " + str(len(keyword_list)))
for keyword, code in zip(keyword_list, code_list):
    try:
        num += 1

        response = requests.get(url + '?item_id=' + keyword, headers={'User-Agent': 'Mozilla/5.0'})
        data = response.text
        print(type(data))
        # if num > 10:
        #     break
        sleep(0.5)
        print(num, {'keyword': keyword, 'stock_code': code, 'data': data})
        data_list.append({'keyword': keyword, 'stock_code': code, 'data': data})

    except Exception as e:
        print(e)
        continue

with open("data_2.pickle", "wb") as fw:
    pickle.dump(data_list, fw)

with open("data_2.pickle", "rb") as fw:
    data = pickle.load(fw)

print(data)

