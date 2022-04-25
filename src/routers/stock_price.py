import datetime as dt
import FinanceDataReader as fdr
import numpy
import numpy as np
import json
import pandas as pd
from tqdm import tqdm
from fastapi import APIRouter

router = APIRouter(
    prefix="/v1/stock",
    tags=["stock"],
    responses={404: {"description": "Not found"}},
)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)  # 데이터 프레임 생략(...)없이 출력

KOSDAQ_list = fdr.StockListing("KOSDAQ")  # 코스닥 상장 종목 코드 리스팅
KOSPI_list = fdr.StockListing("KOSPI")
KOS_list = KOSDAQ_list.append(KOSPI_list)

COLUMN_LIST = {"code": [None], "name": [None], "date": [None],
               "open": [None], "high": [None], "low": [None], "close": [None], "volume": [None],
               "price_change": [None], "volume_change": [None],
               "sma_5": [None], "sma_10": [None], "sma_20": [None], "sma_60": [None], "sma_120": [None],
               "sma_5_change": [None]}

today = dt.datetime.today()  # 금일의 날짜 데이터
one_year = dt.timedelta(days=365)  # 지난 1년간의 데이터를 가져오기 위한 시간변화량
year_before = today - one_year


def append_data(last_date, code):
    df = fdr.DataReader(code, year_before.strftime("%Y-%m-%d"))
    # 해당 종목 코드의 금일로부터 지난 1년간의 주식 데이터 수집

    close_date = df.index[-1].date()  # 장이 마지막으로 마감한 날짜

    print("Last close date: ", close_date.strftime("%Y-%m-%d"))

    start = dt.datetime.strptime(last_date, "%Y-%m-%d") + dt.timedelta(1)
    start = start.date()

    for i in tqdm(range((close_date - start).days, -1, -1)):

        t_row = pd.DataFrame(COLUMN_LIST)  # temporary row

        t_row.iloc[0, 0] = code  # code

        name = KOS_list[KOS_list['Symbol'] == code].iloc[0, 2]
        t_row.iloc[0, 1] = name  # name

        t_row.iloc[0, 2] = (close_date - dt.timedelta(i)).strftime("%Y-%m-%d")  # date

        for k in range(0, 6):
            t_row.iloc[0, k + 3] = df.iloc[-1 - i, k]
        # t_row.iloc[0, 2] = df.iloc[-1-i, 0]  # open
        # t_row.iloc[0, 3] = df.iloc[-1-i, 1]  # high
        # t_row.iloc[0, 4] = df.iloc[-1-i, 2]  # low
        # t_row.iloc[0, 5] = df.iloc[-1-i, 3]  # close
        # t_row.iloc[0, 6] = df.iloc[-1-i, 4]  # volume
        # t_row.iloc[0, 7] = df.iloc[-1-i, 5]  # change

        if len(df["Volume"]) > 2:
            yd_volume = df.iloc[-2 - i, 4]
            td_volume = df.iloc[-1 - i, 4]
            if yd_volume != 0:
                volume_change = (td_volume - yd_volume) / yd_volume * 100
                t_row.iloc[0, 9] = volume_change

        if len(df["Close"]) > 5:
            sma_5 = np.mean(df.iloc[-1 - i:-6 - i:-1, 3])
            t_row.iloc[0, 10] = sma_5
            if len(df["Close"]) > 10:
                sma_10 = np.mean(df.iloc[-1 - i:-11 - i:-1, 3])
                t_row.iloc[0, 11] = sma_10
                if len(df["Close"]) > 20:
                    sma_20 = np.mean(df.iloc[-1 - i:-21 - i:-1, 3])
                    t_row.iloc[0, 12] = sma_20
                    if len(df["Close"]) > 60:
                        sma_60 = np.mean(df.iloc[-1 - i:-61 - i:-1, 3])
                        t_row.iloc[0, 13] = sma_60
                        if len(df["Close"]) > 120:
                            sma_120 = np.mean(df.iloc[-1 - i:-121 - i:-1, 3])
                            t_row.iloc[0, 14] = sma_120

        sma_5_y = np.mean(df.iloc[-2 - i:-7 - i:-1, 3])  # 전일 5 이평선
        sma_5_change = (sma_5 - sma_5_y) / sma_5_y
        t_row.iloc[0, 15] = sma_5_change

        if i == (close_date - start).days:
            result = t_row
        else:
            result = pd.concat([result, t_row])

    result = result.to_dict('list')
    for r in result.keys():
        if type(result[r][0]) is numpy.int64:
            result[r] = [int(i) for i in result[r]]
        elif type(result[r][0]) is numpy.float64:
            result[r] = [float(i) for i in result[r]]

    return result


@router.get("/price")
async def get_stock_price(last_date: str, code: str):
    return append_data(last_date, code)
