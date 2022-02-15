from concurrent import futures
from datetime import datetime
from domain.query import SEQuery
from fastapi import FastAPI
from newspaper import Article
from urllib.parse import quote
import re
import requests

app = FastAPI()
url = "https://www.sedaily.com"
MAX_WORKERS = 20

@app.get("/")
def read_root():
    return {"crawler": "isWorking"}


@app.post("/v1/articles/seouleco")
def getSEArticle(query: SEQuery):
    requestUrl = makeSearchSEUrl(query)
    # UA가 없으면 403 에러 발생
    response = requests.get(requestUrl, headers={'User-Agent': 'Mozilla/5.0'})

    html = response.content.decode('utf-8')

    r = re.compile("(/NewsView/\w+)\"")
    linkResult = r.findall(html)

    dateR = re.compile("<span class=\"date\">(\d{4}.\d{2}.\d{2})</span>")
    dateResult = dateR.findall(html)

    timeR = re.compile("<span class=\"time\">(\d{2}:\d{2}:\d{2})</span>")
    timeResult = timeR.findall(html)

    workers = min(MAX_WORKERS, len(linkResult))
    with futures.ThreadPoolExecutor(workers) as executor:
        articleResult = list(executor.map(parseArticle, linkResult))

    resultList = []
    for i in range(len(linkResult)):
        resultList.append({
            "link": url + linkResult[i],
            "datetime": dateResult[i] + ' ' + timeResult[i],
            "article": articleResult[i]
        })
    return {
        "result": resultList
    }


@app.post("/v1/search/seouleco")
def searchSE(query: SEQuery):
    requestUrl = makeSearchSEUrl(query)
    # UA가 없으면 403 에러 발생
    response = requests.get(requestUrl, headers={'User-Agent': 'Mozilla/5.0'})

    return {
        "Page": query.page,
        "scDetail": query.scDetail,
        "scOrdBy": query.scOrdBy,
        "catView": query.catView,
        "scText": quote(query.scText),
        "scPeriod": query.scPeriod,
        "scArea": query.scArea,
        "scTextIn": quote(query.scTextIn),
        "scTextExt": quote(query.scTextExt),
        "scPeriodS": query.scPeriodS,
        "scPeriodE": query.scPeriodE,
        "command": query.command,
        "_": int(datetime.now().timestamp()),
        "result": response.content.decode('utf-8')
    }


def makeSearchSEUrl(query):
    paraList = [
        "Page=" + str(query.page),
        "scDetail=" + query.scDetail,
        "scOrdBy=" + str(query.scOrdBy),
        "catView=" + query.catView,
        "scText=" + quote(query.scText),
        "scPeriod=" + query.scPeriod,
        "scText=" + quote(query.scText),
        "scPeriod=" + query.scPeriod,
        "scArea=" + query.scArea,
        "scTextIn=" + quote(query.scTextIn),
        "scTextExt=" + quote(query.scTextExt),
        "scPeriodS=" + query.scPeriodS,
        "scPeriodE=" + query.scPeriodE,
        "command=" + query.command,
        "_=" + str(int(datetime.now().timestamp()))
    ]
    return url + '/Search/Search/SEList?' + '&'.join(paraList)


def parseArticle(path):
    article = Article(url + path, language='ko')
    article.download()
    article.parse()
    print(article.title)
    return {
        "title": article.title,
        "text": article.text,
        "publishDate": article.publish_date
    }
