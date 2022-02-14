from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
import requests
from urllib.parse import quote

app = FastAPI()
url = "https://www.sedaily.com/Search/Search/SEList?"


class Query(BaseModel):
    page: int
    scDetail: str = "detail"
    scOrdBy: int = 0
    catView: str = "AL"
    scText: str
    scPeriod: str = "6m"
    scArea: str = "tc"
    scTextIn: str = ""
    scTextExt: str = ""
    scPeriodS: str = ""
    scPeriodE: str = ""
    command: str = ""
    _: int = int(datetime.now().timestamp())


@app.get("/")
def read_root():
    return {"seoul_eco_crawler": "isWorking"}


@app.post("/v1/search")
def search(query: Query):
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

    requestUrl = url + '&'.join(paraList)

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
