#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 09:49:17 2019

@author: ivancalderon
"""

# %%
import requests
import pandas as pd
import subprocess
import os
import datetime as dt
import numpy as np
import asyncio


# %%
def get_data_path():
    """
    Get path to alphavantage.co data API\n
    The API path needs and API key.\n
    Please check the documentation:\n
    https://www.alphavantage.co/documentation/
    """
    source = "https://www.alphavantage.co/query?function={}&symbol={}&outputsize={}&apikey=YOURKEY"
    a = "symbol={}&outputsize"
    b = "symbol={}&interval={}&outputsize"
    return {'intraday': source.replace(a, b), 'daily': source}


path_dict = get_data_path()
# %%


def pull_data(timeframe, stock, size, freq=None):
    """
    Pull price action data from alphavantage.co\n
    timeframe: string, two options 'daily' or 'intraday'\n
    stock: string, ticker of the stock\n
    size: string, two options 'full' or 'compact'\n
    freq: int, type of minute chart. One of 1, 5, 15, 30, 60\n
    """
    functions = {"daily": "TIME_SERIES_DAILY",
                 "intraday": "TIME_SERIES_INTRADAY"
                 }
    path = path_dict[timeframe]
    print(f'Path {timeframe} served from dictionary')
    if timeframe == "intraday":
        if freq is None:
            raise ValueError("If timeframe is intraday, freq must be given")
        else:
            interval = f'{freq}min'
            path = path.format(functions[timeframe],
                               stock.upper(),
                               interval,
                               size)
    elif timeframe == "daily":
        path = path.format(functions[timeframe],
                           stock.upper(),
                           size)
    data = requests.get(path).json()
    series = list(data.keys())[1]
    df = pd.DataFrame.from_dict(data[series],
                                orient="index"
                                )
    df.columns = ["Open", "High", "Low", "Close", "Volume"]
    df = df.astype({"Open": float,
                    "High": float,
                    "Low": float,
                    "Close": float,
                    "Volume": float
                    },
                   copy=False
                   )
    df.index = pd.to_datetime(df.index)
    return df


# %%
async def pull_async(timeframe, stock, size, freq=None):
    await asyncio.sleep(0)
    mydf = pull_data(timeframe, stock, size, freq)
    return mydf


def task_manager(ticker):
    ticker = ticker.upper()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = [
            asyncio.ensure_future(pull_async("intraday", ticker, "full", 15)),
            asyncio.ensure_future(pull_async("daily", ticker, "compact"))
            ]
    try:
        loop.run_until_complete(asyncio.gather(*tasks))
    except RuntimeError:
        pass
    loop.close()
    return {"intraday": tasks[0],
            "daily": tasks[1]}


# %%
def clear_repeated(array):
    if 1 not in array:
        return array
    case1 = np.array([0, 1, 1])
    case2 = np.array([0, 0, 1])
    case3 = np.array([0, 0, 0])
    pointer = {0: case1,
               1: case2,
               2: case3
               }
    position = list(array).index(1)
    x = array - pointer[position]
    return x


# %%
def test_time_range(x):
    fifteen = dt.time(9, 45)
    half = dt.time(10, 00)
    hour = dt.time(10, 30)
    compare = np.array([fifteen,
                        half,
                        hour
                        ]
                       )
    # use *1 to convert array of bools to int
    y = (x.time() <= compare)*1
    return clear_repeated(y)


# %%
def expected_move(df, timeframe):
    if timeframe not in ["daily", "intraday"]:
        raise ValueError("timeframe not accepted")
    if timeframe == "intraday":
        point = dt.time(10, 30)
        move = df[df.index.time <= point].copy()
    elif timeframe == "daily":
        move = df
    move.loc[:, "Range"] = move["High"] - move["Low"]
    return move


# %%
def first_hour_peak(df):
    """
    df : intraday(15min) dataframe with stock price\n
    return:
        times highs or lows happen in the 1st hour
    """
    y = df.groupby(pd.Grouper(freq="B"))
    hole = []
    for day in y:
        x = day[1]
        try:
            hole.append(x.idxmax())
        except ValueError:
            pass
    m = pd.DataFrame(hole)[["High", "Low"]]
    h = m["High"].apply(test_time_range).sum() / m["High"].count() * 100
    l = m["Low"].apply(test_time_range).sum() / m['Low'].count() * 100
    return (h, l)


# %%
def week_day_move(df):
    """
    df: daily timeframe stock prices.\n
    return:
        range by day of the week
    """
    df.loc[:, 'week_day'] = df.index.day_name()
    df.loc[:, "Range"] = df["High"] - df["Low"]
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    data = {x: df.loc[df['week_day']== x] for x in days}
    return data
