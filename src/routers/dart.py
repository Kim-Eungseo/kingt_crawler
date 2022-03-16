import datetime

from fastapi import APIRouter
from newspaper import Article

import requests
import re

router = APIRouter(
    prefix="/v1/dart",
    tags=["dart"],
    responses={404: {"description": "Not found"}},
)
url = "https://dart.fss.or.kr"

'''
 WARNING!!
 This API needs new SESSION_ID everytime manually.
'''


@router.get("/articles")
async def get_dart_article(item_id: str = ""):
    request_url = make_code_dart_url()
    # UA가 없으면 403 에러 발생
    try:


        response = requests.post(request_url, headers={'User-Agent': 'Mozilla/5.0'}
                                 , data={'textCrpNm': item_id}, cookies={
                'WMONID': 'ReBB0nMFxMF', 'JSESSIONID': '8f4LoOu9rZZ5yXKCTcKqQiyCqHl1CgnblKJFSoop1QXLON47724P6EyaXJeY9xHN'
                                                       '.ZG1fZGFydC9kYXJ0MV9kYXJ0X21zMw== '})
        item_code = response.content.decode('utf-8')

        response = requests.get(make_gongsi_dart_url(item_id, item_code), headers={'User-Agent': 'Mozilla/5.0'}
                                , cookies={'WMONID': 'ReBB0nMFxMF',
                                           'JSESSIONID': '8f4LoOu9rZZ5yXKCTcKqQiyCqHl1CgnblKJFSoop1QXLON47724P6EyaXJeY9xHN'
                                                         '.ZG1fZGFydC9kYXJ0MV9kYXJ0X21zMw== '})

        # print(response.content.decode('utf-8'))
        r = re.compile('/report\S+show')
        caption_url = r.findall((response.content.decode('utf-8')))[0]

        # response = requests.get(url + caption_url, headers={'User-Agent': 'Mozilla/5.0'}
        #                         , cookies={'WMONID': 'ReBB0nMFxMF',
        #                                    'JSESSIONID': '8f4LoOu9rZZ5yXKCTcKqQiyCqHl1CgnblKJFSoop1QXLON47724P6EyaXJeY9xHN'
        #                                                  '.ZG1fZGFydC9kYXJ0MV9kYXJ0X21zMw== '})
        #
        # item_caption = response.text
        # print(item_caption)
        # return item_caption

        article = Article(url + caption_url, language='ko')
        article.download()
        article.parse()

        return {
            "item_id": item_id,
            "text": article.text,
            "publishDate": datetime.datetime.now()
        }
    except Exception as e:
        return {
            'error': str(e)
        }


def make_code_dart_url() -> str:
    return url + '/corp/searchExistAll.ax'


def make_gongsi_dart_url(item_id, item_code) -> str:
    return url + '/navi/searchNavi.do?naviCrpNm=' + str(item_id) \
           + "&naviCrpCik=" + str(item_code) + '&naviCode=A002'
