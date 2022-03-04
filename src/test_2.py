import json
import pandas as pd
from konlpy.tag import Okt
from tqdm import tqdm
import pickle

train_list = []
preprocessed_data = []

kor_stopwords = pd.read_csv("kor_stopwords.txt", sep="\t", names=['stw', 'part', 'ratio'])

with open('./donga.json') as json_file:
    json_data = json.load(json_file)

    # 문자열
    # key가 json_string인 문자열 가져오기
    article_list = json_data["result"]

    for i in article_list:
        train_list.append(i['article']['text'])

train_series = pd.Series(train_list)
train_series = train_series.str.replace("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]", "")

okt = Okt()

for sentence in tqdm(train_series):
    tokenized_sent = okt.morphs(sentence, stem=True)
    stw_rem_sent = [word for word in tokenized_sent if not word in kor_stopwords['stw']]
    preprocessed_data.append(stw_rem_sent)

my_list = ['a', 'b', 'c']

with open("data.pickle", "wb") as fw:
    pickle.dump(preprocessed_data, fw)
