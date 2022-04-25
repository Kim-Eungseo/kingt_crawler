import pickle
import json
import re

with open('../data_3.pickle', 'rb') as fr:
    data = pickle.load(fr)

new_data = []
# print(data)
for idx, d in enumerate(data):
    if '"error"' not in d['data']:

        d['data'] = json.loads(d['data'])
        d['data']['text'] = d['data']['text'].replace('\n', ' ').replace('"', '')
        new_data.append(d)
        # print(d['data'])

with open("dart.json", "w") as fw:
    json.dump(new_data, fw)

with open("dart.json", "rb") as rb:
    data = json.load(rb)
