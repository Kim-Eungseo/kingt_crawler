from concurrent import futures
from newspaper import Article
from urllib.parse import quote
from fastapi import APIRouter
from pydantic import BaseModel

import re
import requests

router = APIRouter(
    prefix="/v1/seouleco",
    tags=["seouleco"],
    responses={404: {"description": "Not found"}},
)
url = "https://www.chosun.com"
MAX_WORKERS = 20


class ChoQuery(BaseModel):
    keyword: str
    period: int
    page: int = 1
    start_date: str
    end_date: str
    include: str
    exclude: str


@router.post("/articles")
async def getChoArticle(query: ChoQuery):
    requestUrl = makeSearchChoUrl(query)
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


# period: 2 = Week, 3 = Month, 4 = Year 5 = Custom, date format = YYYYMMDD
def makeSearchChoUrl(query):
    per_val = ''
    if query.period == 0:
        per_val = 'all'
    elif query.period == 2:
        per_val = "1w"
    elif query.period == 3:
        per_val = "1m"
    elif query.period == 4:
        per_val = "1y"
    elif query.period == 5:
        per_val = "direct"

    return 'https://www.chosun.com/nsearch/?query={0}&page={1}&siteid=&sort=1&date_period={2}&date_start={' \
           '3}&date_end={4}&writer=&field=&emd_word={5}&expt_word={6}&opt_chk=true&app_check=0&website=www,' \
           'chosun&category=' \
        .format(query.keyword, query.page, per_val, query.start_date, query.end_date, query.include, query.exclude)


def parseArticle(path):
    article = Article(url + path, language='ko')
    article.download()
    article.parse()

    return {
        "title": article.title,
        "text": article.text,
        "publishDate": article.publish_date
    }
