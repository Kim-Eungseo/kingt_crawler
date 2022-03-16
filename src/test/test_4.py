import pickle
import json

with open('../data_2.pickle', 'rb') as fr:
    data = pickle.load(fr)
errors = []

for d in data:
    if '"error"' in d['data']:
        errors.append(d['data'])

for i in errors:
    print(i)


