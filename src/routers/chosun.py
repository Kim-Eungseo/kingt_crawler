from concurrent import futures
from newspaper import Article
from urllib.parse import quote, urlencode
from fastapi import APIRouter
from pydantic import BaseModel

import re
import json
import requests

router = APIRouter(
    prefix="/v1/chosun",
    tags=["chosun"],
    responses={404: {"description": "Not found"}},
)
url = "https://www.chosun.com"
MAX_WORKERS = 20


class ChoQuery(BaseModel):
    category: str = ""
    date_end: str
    date_period: str = "all"
    date_start: str
    emd_word: str = ""
    encodeURL: str = "true"
    expt_word: str = ""
    field: str = ""
    limitedPage: int = 400
    page: int = 0
    query: str
    siteid: str
    sort: str = "0"
    writer: str = ""


@router.post("/articles")
async def getChoArticle(query: ChoQuery) -> str:
    requestUrl = makeSearchChoUrl(query)
    # UA가 없으면 403 에러 발생
    response = requests.get(requestUrl, headers={'User-Agent': 'Mozilla/5.0'})

    return json.loads(response.content.decode('utf-8'))


# period: 2 = Week, 3 = Month, 4 = Year 5 = Custom, date format = YYYYMMDD
def makeSearchChoUrl(query=None) -> str:
    queryStr = {
        "category": query.category,
        "date_end": query.date_end,
        "date_period": query.date_period,
        "date_start": query.date_start,
        "emd_word": query.emd_word,
        "encodeURI": query.encodeURL,
        "expt_word": query.expt_word,
        "field": query.field,
        "limitedPage": query.limitedPage,
        "page": query.page,
        "query": query.query,
        "siteid": query.siteid,
        "sort": query.siteid,
        "writer": query.writer
    }

    qs = json.dumps(queryStr, ensure_ascii=False)

    return 'https://www.chosun.com/pf/api/v3/content/fetch/search-param-api?query=' \
           + qs + '&d=753&website=chosun'


def parseArticle(path):
    article = Article(url + path, language='ko')
    article.download()
    article.parse()

    return {
        "title": article.title,
        "text": article.text,
        "publishDate": article.publish_date
    }

