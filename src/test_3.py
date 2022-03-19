import requests
import json
import pickle
from time import sleep

with open("corp_list.pickle", "rb") as fr:
    data = pickle.load(fr)

keyword_list = list(data['corp_name'])
code_list = list(data['stock_code'])

url = "http://localhost:8000/v1/dart/articles"
num = 909
with open("data_2.pickle", "rb") as fw:
    data_list = pickle.load(fw)

print("key length " + str(len(keyword_list)))
for keyword, code in zip(keyword_list[910:1062], code_list[910:1062]):
    try:
        num += 1

        response = requests.get(url + '?item_id=' + code, headers={'User-Agent': 'Mozilla/5.0'})
        data = response.text
        if "HTTPSConnection" in data:
            sleep(0.4)
            response = requests.get(url + '?item_id=' + code, headers={'User-Agent': 'Mozilla/5.0'})

        print(type(data))
        # if num > 10:
        #     break
        sleep(0.2)
        print(num, {'keyword': keyword, 'stock_code': code, 'data': data})
        data_list[num] = {'keyword': keyword, 'stock_code': code, 'data': data}

    except Exception as e:
        print(e)
        continue

with open("data_3.pickle", "wb") as fw:
    pickle.dump(data_list, fw)


print(data)

