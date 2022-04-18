import datetime as dt
import FinanceDataReader as fdr
import numpy as np
import pandas as pd
import re

pd.set_option('display.max_rows', None);
pd.set_option('display.max_columns', None)  # 데이터 프레임 생략(...)없이 출력

KOSDAQ_list = list(fdr.StockListing("KOSDAQ")['Symbol'])  # 코스닥 상장 종목 코드 리스팅
KOSPI_list = list(fdr.StockListing("KOSPI")['Symbol'])
KOS_list = KOSDAQ_list + KOSPI_list

code_re = re.compile("\d{6}")
valid_kos_code = []  # 최종 valid code

for s in KOSDAQ_list:
    print(s)

for i in range(len(KOS_list)):
    if code_re.match(KOS_list[i]) and len(KOS_list[i]) == 6:
        valid_kos_code.append(KOS_list[i])

KOS_list = valid_kos_code

now_day = dt.datetime.today()  # 금일의 날짜 데이터
print(now_day.strftime("%Y-%m-%d"))
one_year = dt.timedelta(days=365)  # 지난 1년간의 데이터를 가져오기 위한 시간변화량

COLUMN_LIST = {"code": [], "date": [],
               "open": [], "high": [], "low": [], "close": [], "volume": [], "change": [],
               "sma_5": [], "sma_10": [], "sma_20": [], "sma_60": [], "sma_120": [],
               "align": [], "goldenX": [], "deadX": [], "volume_change": [],
               "is_ceiling": [], "is_floor": [], "is_inverted_hammer": [], "new_high_52": [], "new_low_52": [],
               "bol_upper_20": [], "bol_lower_20": []
               }

COLUMN_LIST_NaN = {"code": [np.nan], "date": [np.nan],
                   "open": [np.nan], "high": [np.nan], "low": [np.nan], "close": [np.nan], "volume": [np.nan],
                   "change": [np.nan],
                   "sma_5": [np.nan], "sma_10": [np.nan], "sma_20": [np.nan], "sma_60": [np.nan], "sma_120": [np.nan],
                   "align": [np.nan], "goldenX": [np.nan], "deadX": [np.nan], "volume_change": [np.nan],
                   "is_ceiling": [np.nan], "is_floor": [np.nan], "is_inverted_hammer": [np.nan],
                   "new_high_52": [np.nan], "new_low_52": [np.nan],
                   "bol_upper_20": [np.nan], "bol_lower_20": [np.nan]
                   }


# 칼럼 리스트. 추가 및 삭제 가능


def append(start, end=None):
    if start is not None and end is None:
        end = now_day
    else:
        end = dt.datetime.strptime(latest, "%Y-%m-%d")

    result = pd.DataFrame(COLUMN_LIST)

    start = dt.datetime.strptime(last, "%Y-%m-%d")

    for day in range(0, (end - start).days):
        obj_day = start + dt.timedelta(days=day + 1)  # "+ 1 은 익일
        past_day = obj_day - one_year

        for i in range(0, 100):

            code = KOS_list[i]
            if (code[2] or code[3]).isalpha() == 1 or len(code) != 6:
                continue

            df = fdr.DataReader(code, past_day.strftime("%Y-%m-%d"), obj_day.strftime("%Y-%m-%d"))
            # 해당 종목 코드의 목표일로부터 지난 1년간의 주식 데이터 수집

            if len(df["Close"]) == 0:
                continue

            t_row = pd.DataFrame(COLUMN_LIST_NaN)  # temporary row

            t_row.iloc[0, 0] = code  # code

            t_row.iloc[0, 1] = obj_day.strftime("%Y-%m-%d")  # date
            for k in range(0, 6):
                if df.iloc[-1, k] == 0:
                    t_row.iloc[0, k + 2] = np.nan
                else:
                    t_row.iloc[0, k + 2] = df.iloc[-1, k]

            # t_row.iloc[0, 2] = df.iloc[-1, 0]  # open
            # t_row.iloc[0, 3] = df.iloc[-1, 1]  # high
            # t_row.iloc[0, 4] = df.iloc[-1, 2]  # low
            # t_row.iloc[0, 5] = df.iloc[-1, 3]  # close
            # t_row.iloc[0, 6] = df.iloc[-1, 4]  # volume
            # t_row.iloc[0, 7] = df.iloc[-1, 5]  # change

            # n 일간의 종가단순이동평균
            sma_5 = np.nan;
            sma_10 = np.nan;
            sma_20 = np.nan;
            sma_60 = np.nan;
            sma_120 = np.nan

            if len(df["Close"]) > 5:
                sma_5 = np.mean(df.iloc[-1:-6:-1, 3])
                if len(df["Close"]) > 10:
                    sma_10 = np.mean(df.iloc[-1:-11:-1, 3])
                    t_row.iloc[0, 9] = sma_10
                    if len(df["Close"]) > 20:
                        sma_20 = np.mean(df.iloc[-1:-21:-1, 3])
                        t_row.iloc[0, 10] = sma_20
                        if len(df["Close"]) > 60:
                            sma_60 = np.mean(df.iloc[-1:-61:-1, 3])
                            t_row.iloc[0, 11] = sma_60
                            if len(df["Close"]) > 120:
                                sma_120 = np.mean(df.iloc[-1:-121:-1, 3])
                                t_row.iloc[0, 12] = sma_120

            # print("\n종가단순이동평균 5: {}, 10: {}\n20:{}, 60:{}, 120:{}\n".format(sma_5, sma_10, sma_20, sma_60, sma_120))

            # 정배열 여부
            align = 0
            if sma_5 > sma_10 > sma_20 > sma_60 > sma_120:
                align = 1
            t_row.iloc[0, 13] = align  # align

            # 골든크로스 여부, 데드크로스 여부 (20, 60 종가단순이동평균 이용)
            goldenX = 0;
            deadX = 0
            if sma_20 > sma_60:
                goldenX = 1
            elif sma_20 < sma_60:
                deadX = 1
            t_row.iloc[0, 14] = goldenX  # goldenX
            t_row.iloc[0, 15] = deadX  # deadX

            # print("\n20, 60 종가단순이동평균: {}, {}".format(sma_20, sma_60))
            # print("goldenX: {}, deadX: {}\n".format(goldenX, deadX))

            if len(df["Volume"]) > 2:
                yd_volume = df.iloc[-2, 4]
                td_volume = df.iloc[-1, 4]
                if yd_volume != 0:
                    volume_change = (td_volume - yd_volume) / yd_volume * 100
                    t_row.iloc[0, 16] = volume_change
            # print("\n전일 거래량: {}, 금일 거래량: {}\n전일대비 거래대금 증감비율: {}%\n".format(yd_volume, td_volume, round(volume_change, 3)))

            # td_price = df.iloc[-1, 3]; yd_price = df.iloc[-2, 3]  # 금일종가, 전일종가
            # price_change = (td_price - yd_price) / yd_price * 100
            #
            # # print("\n가격증감률: {}%".format(round(price_change, 3)))

            is_ceiling = 0;
            is_floor = 0
            if df.iloc[-1, 5] * 100 == 30:
                is_ceiling = 1
            elif df.iloc[-1, 5] * 100 == -30:
                is_floor = 1
            t_row.iloc[0, 17] = is_ceiling  # is_ceiling
            t_row.iloc[0, 18] = is_floor  # is_floor

            is_inverted_hammer = 0
            t_row.iloc[0, 19] = is_inverted_hammer

            # print("상한가, 하한가 발생여부: {}, {}\n".format(is_ceiling, is_floor))
            new_high_52 = 0;
            new_low_52 = 0
            if len(df["Close"]) > 364:
                if df.iloc[-1, 1] > np.max(df.iloc[0:-1, 1]):
                    new_high_52 = 1
                if df.iloc[-1, 2] < np.min(df.iloc[0:-1, 2]):
                    new_low_52 = 1
            t_row.iloc[0, 20] = new_high_52  # new_high_52
            t_row.iloc[0, 21] = new_low_52  # new_low_52

            if sma_20 != np.nan:
                bol_upper_20 = sma_5 + np.std(df.iloc[-1:-21:-1, 3]) * 2
                bol_lower_20 = sma_5 - np.std(df.iloc[-1:-21:-1, 3]) * 2
                t_row.iloc[0, 22] = bol_upper_20  # bol_upper_20
                t_row.iloc[0, 23] = bol_lower_20  # bol_lower_20

            result = pd.concat([result, t_row])

    return result


CUSTOM_FRAME = pd.DataFrame(COLUMN_LIST)

print("date format: YYYY-MM-DD")  # dateutil 클래스 parse 쓸 수 있음
last = input("last date: ")
latest = input("latest date(blank will mean today): ")
if latest == '':
    CUSTOM_FRAME = CUSTOM_FRAME.append(append(last))
else:
    CUSTOM_FRAME = CUSTOM_FRAME.append(append(last, latest))

print(CUSTOM_FRAME)
