from concurrent import futures
from newspaper import Article
from fastapi import APIRouter
from pydantic import BaseModel
from bs4 import BeautifulSoup as Soup

import re
import requests

router = APIRouter(
    prefix="/v1/donga",
    tags=["donga"],
    responses={404: {"description": "Not found"}},
)
url = "https://www.donga.com/"
MAX_WORKERS = 20


class DAQuery(BaseModel):
    page: int = 1
    keyword: str = ""
    start_date: str = ""
    end_date: str = ""
    check_news: int = 1
    more: int = 1
    sorting: int = 1
    _range: int = 2


@router.get("/articles")
async def get_da_article(query: DAQuery):
    requestUrl = url + '?' + 'query=' + query.keyword
    # UA가 없으면 403 에러 발생
    response = requests.get(requestUrl, headers={'User-Agent': 'Mozilla/5.0'})

    if response.status_code == 200:
        html = response.content.decode('utf-8')
        soup = Soup(html, "lxml")
        search_list = soup.find_all("div", "searchList")

        link_r = re.compile("(https://www.donga.com/news/article/all/\w)\"\s")
        date_r = re.compile("<span>(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2})</span>")

        link_result, date_result = [], []

        for i in search_list:
            link_result.append(str(link_r.find(str(i))))
            date_result.append(str(date_r.find(str(i))))

        workers = min(MAX_WORKERS, len(link_result))
        with futures.ThreadPoolExecutor(workers) as executor:
            article_result = list(executor.map(parse_article, link_result))

        result_list = []
        for i in range(len(link_result)):
            result_list.append({
                "link": url + link_result[i],
                "datetime": date_result[i],
                "article": article_result[i]
            })
        return {
            "result": result_list
        }
    else:
        print(response.status_code)


# period: 2 = Week, 3 = Month, 4 = Year 5 = Custom, date format = YYYYMMDD
def make_search_cho_url(query) -> str:
    return url + '/news/search?p={0}&query={1}&check_news={2}&more={3}&sorting={4}&search_date={5}&v1={6}' \
                 '&v2={7}&range={8} '.format((query.page - 1) * 15 + 1, query.keyword, query.check_news,
                                             query.more, query.sorting, query.search_date,
                                             query.start_date, query.end_date, query.range)


def parse_article(link):
    article = Article(link, language='ko')
    article.download()
    article.parse()

    return {
        "title": article.title,
        "text": article.text,
        "publishDate": article.publish_date
    }