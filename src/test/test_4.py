import pickle
import json

with open('../data_3.pickle', 'rb') as fr:
    data = pickle.load(fr)
errors = []

for d in data:
    if '"error"' in d['data']:
        # if d['keyword'] == 'SK':
        #     print(d)
        errors.append(d['keyword'])

for i in errors:
    print(i)

print(len(errors))

