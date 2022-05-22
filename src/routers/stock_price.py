import datetime as dt
import FinanceDataReader as fdr
from multiprocessing import Pool
import numpy
import numpy as np
import math
import json
import pandas as pd
from tqdm import tqdm
import re
from fastapi import APIRouter

router = APIRouter(
    prefix="/v1/stock",
    tags=["stock"],
    responses={404: {"description": "Not found"}},
)

# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)  # 데이터 프레임 생략(...)없이 출력

KOSDAQ_list = fdr.StockListing("KOSDAQ")  # 코스닥 상장 종목 코드 리스팅 - 업데이트 해야 하는 전역변수
KOSPI_list = fdr.StockListing("KOSPI")
KOS_list = KOSDAQ_list.append(KOSPI_list)
#
# code_re = re.compile("\d{6}")  # valid code를 잡아내기 위한 정규표현식
# valid_kos_code = []  # valid code
#
# for i in tqdm(range(len(KOS_list))):
#     if code_re.match(KOS_list.iloc[i, 0]) and len(KOS_list.iloc[i, 0]) == 6:
#         valid_kos_code.append(KOS_list.iloc[i, 0])

COLUMN_LIST = {"code": [None], "name": [None], "date": [None],
               "open": [None], "high": [None], "low": [None], "close": [None], "volume": [None],
               "price_change": [None], "volume_change": [None],
               "sma_5": [None], "sma_10": [None], "sma_20": [None], "sma_60": [None], "sma_120": [None],
               "sma_5_change": [None]}


whole_db = {}
dist_matrix_price = []
dist_matrix_sma_5 = []


def year_before():

    today = dt.datetime.today()  # 금일의 날짜 데이터
    one_year = dt.timedelta(days=365)  # 지난 1년간의 데이터를 가져오기 위한 시간변화량

    return today - one_year


def update_kos():

    KOSDAQ_list = fdr.StockListing("KOSDAQ")
    KOSPI_list = fdr.StockListing("KOSPI")
    KOS_list = KOSDAQ_list.append(KOSPI_list)

    return KOS_list


def append_data(last_date, code):
    KOS_list = update_kos()
    df = fdr.DataReader(code, year_before().strftime("%Y-%m-%d"))
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


def compose_db(code: str) -> (str, dict):
    yb = year_before()
    df = fdr.DataReader(code, yb.strftime("%Y-%m-%d"))
    sma_5_list = []
    if len(df) > 20:
        for i in range(0, 20):
            sma_5 = np.mean(df.iloc[-1 - i:-6 - i:-1, 3])
            sma_5_y = np.mean(df.iloc[-2 - i:-7 - i:-1, 3])
            sma_5_change = (sma_5 - sma_5_y) / sma_5_y * 100
            sma_5_list.append(sma_5_change)
        sma_5_list.reverse()

        price_change = list(df.iloc[-1:-21:-1, 5])
        price_change.reverse()
        price_list = [rate * 100 for rate in price_change]

        result = {
            "name": KOS_list[KOS_list['Symbol'] == code].iloc[0, 2],
            "price": price_list,  # price change
            "sma_5": sma_5_list  # sma_5 change
        }

        return code, result


def initialize_matrix(length):
    matrix = [[np.inf for i in range(length)] for j in range(length)]
    return matrix


def distDTW(ts1, ts2):
    DTW = {}
    for i in range(len(ts1)):
        DTW[(i, -1)] = np.inf
    for i in range(len(ts2)):
        DTW[(-1, i)] = np.inf
    DTW[(-1, -1)] = 0

    for i in range(len(ts1)):
        for j in range(len(ts2)):
            dist = (ts1[i] - ts2[i]) ** 2
            DTW[(i, j)] = dist + min(DTW[(i - 1, j)],
                                     DTW[(i, j - 1)],
                                     DTW[(i - 1, j - 1)])
    return math.sqrt(DTW[len(ts1) - 1, len(ts2) - 1])


def pair_dist_price(codes: list):
    for i in range(len(codes)):
        for j in range(len(codes)):
            dist_matrix_price[i][j] = distDTW(whole_db[codes[i]]["price"], whole_db[codes[j]]["price"])


def pair_dist_sma_5(codes: list):
    for i in range(len(codes)):
        for j in range(len(codes)):
            dist_matrix_sma_5[i][j] = distDTW(whole_db[codes[i]]["sma_5"], whole_db[codes[j]]["sma_5"])


def update():
    KOSDAQ_list = fdr.StockListing("KOSDAQ")  # 코스닥 상장 종목 코드 리스팅
    KOSPI_list = fdr.StockListing("KOSPI")
    KOS_list = KOSDAQ_list.append(KOSPI_list)

    code_re = re.compile("\d{6}")  # valid code를 잡아내기 위한 정규표현식
    valid_kos_code = []  # valid code

    for i in tqdm(range(len(KOS_list))):
        if code_re.match(KOS_list.iloc[i, 0]) and len(KOS_list.iloc[i, 0]) == 6:
            valid_kos_code.append(KOS_list.iloc[i, 0])

    pool = Pool(processes=8)

    codes = []; dics = []

    for coresult in pool.map(compose_db, valid_kos_code):
        if coresult is None:
            continue
        else:
            codes.append(coresult[0])
            dics.append(coresult[1])

    pool.close()
    pool.join()

    for i in range(len(codes)):
        whole_db[codes[i]] = dics[i]

    global dist_matrix_price
    global dist_matrix_sma_5
    dist_matrix_price = initialize_matrix(len(codes))
    dist_matrix_sma_5 = initialize_matrix(len(codes))

    pair_dist_price(codes)
    pair_dist_sma_5(codes)

@router.get("/price")
async def get_stock_price(last_date: str, code: str):
    return append_data(last_date, code)


@router.post("/update")
async def update_db():
    return update()
