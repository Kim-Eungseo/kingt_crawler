import pickle
import json

with open('../data_3.pickle', 'rb') as fr:
    data = pickle.load(fr)

new_data = []
# print(data)
for idx, d in enumerate(data):
    if '"error"' not in d['data']:
        d['data'] = json.loads(d['data'])
        new_data.append(d)

new_data = json.dumps(new_data).encode('utf-8').decode('unicode-escape')

with open("dart.txt", "w") as fw:
    fw.write(new_data)
