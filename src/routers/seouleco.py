from concurrent import futures
from newspaper import Article
from urllib.parse import quote
from fastapi import APIRouter
from datetime import datetime
from pydantic import BaseModel

import re
import requests

router = APIRouter(
    prefix="/v1/seouleco",
    tags=["seouleco"],
    responses={404: {"description": "Not found"}},
)
url = "https://www.sedaily.com"
MAX_WORKERS = 20


class SEQuery(BaseModel):
    page: int = 1
    sc_detail: str = "detail"
    sc_ord_by: int = 0
    cat_view: str = "AL"
    keyword: str = ""
    period: str = "6m"
    sc_area: str = "tc"
    include: str = ""
    exclude: str = ""
    start_date: str = ""
    end_date: str = ""
    command: str = ""
    _: int = int(datetime.now().timestamp())


@router.get("/articles")
async def get_se_article(query: SEQuery):
    request_url = make_search_se_url(query)
    # UA가 없으면 403 에러 발생
    response = requests.get(request_url, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code == 200:
        html = response.content.decode('utf-8')

        r = re.compile("(/NewsView/\w+)\"")
        link_result = r.findall(html)

        date_r = re.compile("<span class=\"date\">(\d{4}.\d{2}.\d{2})</span>")
        date_result = date_r.findall(html)

        time_r = re.compile("<span class=\"time\">(\d{2}:\d{2}:\d{2})</span>")
        time_result = time_r.findall(html)

        workers = min(MAX_WORKERS, len(link_result))
        with futures.ThreadPoolExecutor(workers) as executor:
            article_result = list(executor.map(parse_article, link_result))

        result_list = []
        for i in range(len(link_result)):
            result_list.append({
                "link": url + link_result[i],
                "datetime": date_result[i] + ' ' + time_result[i],
                "article": article_result[i]
            })
        return {
            "result": result_list
        }
    else:
        print(response.status_code)



@router.get("/search")
async def search_se(query: SEQuery):
    requestUrl = make_search_se_url(query)
    # UA가 없으면 403 에러 발생
    response = requests.get(requestUrl, headers={'User-Agent': 'Mozilla/5.0'})

    return {
        "Page": query.page,
        "scDetail": query.sc_detail,
        "scOrdBy": query.sc_ord_by,
        "catView": query.cat_view,
        "scText": quote(query.keyword),
        "scPeriod": query.period,
        "scArea": query.sc_area,
        "scTextIn": quote(query.include),
        "scTextExt": quote(query.exclude),
        "scPeriodS": query.start_date,
        "scPeriodE": query.end_date,
        "command": query.command,
        "_": int(datetime.now().timestamp()),
        "result": response.content.decode('utf-8')
    }


def make_search_se_url(query):
    paraList = [
        "Page=" + str(query.page),
        "scDetail=" + query.sc_detail,
        "scOrdBy=" + str(query.sc_ord_by),
        "catView=" + query.cat_view,
        "scText=" + quote(query.keyword),
        "scPeriod=" + query.period,
        "scText=" + quote(query.keyword),
        "scPeriod=" + query.period,
        "scArea=" + query.sc_area,
        "scTextIn=" + quote(query.include),
        "scTextExt=" + quote(query.exclude),
        "scPeriodS=" + query.start_date,
        "scPeriodE=" + query.end_date,
        "command=" + query.command,
        "_=" + str(int(datetime.now().timestamp()))
    ]
    return url + '/Search/Search/SEList?' + '&'.join(paraList)


def parse_article(path):
    article = Article(url + path, language='ko')
    article.download()
    article.parse()

    return {
        "title": article.title,
        "text": article.text,
        "publishDate": article.publish_date
    }