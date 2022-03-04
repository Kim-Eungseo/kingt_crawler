from concurrent import futures
from newspaper import Article
from urllib.parse import quote
from fastapi import APIRouter
from pydantic import BaseModel
import json

import re
import requests

router = APIRouter(
    prefix="/v1/chosun",
    tags=["chosun"],
    responses={404: {"description": "Not found"}},
)
url = "https://www.chosun.com"
MAX_WORKERS = 8


class ChoQuery(BaseModel):
    keyword: str = ""
    period: int = 1
    page: int = 1
    start_date: str = ""
    end_date: str = ""
    include: str = ""
    exclude: str = ""


@router.get("/articles")
async def get_cho_article(query: ChoQuery):
    request_url = make_search_cho_url(query)
    # UA가 없으면 403 에러 발생
    response = requests.get(request_url, headers={'User-Agent': 'Mozilla/5.0'})

    html = response.content.decode('utf-8')

    return json.loads(html)


# period: 2 = Week, 3 = Month, 4 = Year 5 = Custom, date format = YYYYMMDD
def make_search_cho_url(query):
    query_json = {
        "category": "",
        "date_end": query.end_date,
        "date_period": query.period,
        "date_start": query.start_date,
        "emd_word": quote(query.include),
        "encodeURI": "true",
        "expt_word": quote(query.exclude),
        "field": "",
        "limitedPage": 400,
        "page": query.page,
        "query": query.keyword,
        "siteid": "",
        "sort": "0",
        "writer": ""
    }

    return 'https://www.chosun.com/pf/api/v3/content/fetch/search-param-api?query=' \
           + json.dumps(query_json) + '&d=753&_website=chosun'


def parse_article(path):
    article = Article(url + path, language='ko')
    article.download()
    article.parse()

    return {
        "title": article.title,
        "text": article.text,
        "publishDate": article.publish_date
    }
