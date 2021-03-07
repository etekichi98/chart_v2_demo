# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 09:48:41 2020

@author: kurihara
"""

import os
import numpy as np
import pandas as pd
import mplfinance as mpf
from collections import namedtuple
from decimal import Decimal, ROUND_HALF_EVEN

PriceLimit = namedtuple("PriceLimit", "l h w")
price_limit_table1 = [
    PriceLimit(0, 100, 30),
    PriceLimit(100, 200, 50),
    PriceLimit(200, 500, 80),
    PriceLimit(500, 700, 100),
    PriceLimit(700, 1000, 150),
]
price_limit_table2 = [
    PriceLimit(1000, 1500, 300),
    PriceLimit(1500, 2000, 400),
    PriceLimit(2000, 3000, 500),
    PriceLimit(3000, 5000, 700),
    PriceLimit(5000, 7000, 1000),
    PriceLimit(7000, 10000, 1500),
]

def load_stock_price_csv(path, adjust=True, term=0):
    if os.path.exists(path):
        count = 0
        with open(path) as f:
            for line in f:
                count += 1
        if term>0:
            skips = count - term - 75
        else:
            skips = 0
        df = pd.read_csv(path, header=None, skiprows=skips,
                         names=['Date','Open','High','Low','Close','Volume'], encoding='UTF-8')
    else:
        df = pd.DataFrame([[0, 0, 0, 0, 0, 0]])
        df.columns = ['Date','Open','High','Low','Close','Volume']
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index("Date")
    
    # 株価が0の場合、前日の終値で埋める
    f_zero2nan = lambda x: np.NaN if x==0 else x
    df['Close'] = df['Close'].map(f_zero2nan)
    df = df.fillna(method='ffill')
    if np.isnan(df['Close'][0]):
        df = df.fillna(method='bfill')
    df['Open'] = df['Open'].map(f_zero2nan)
    df['High'] = df['High'].map(f_zero2nan)
    df['Low'] = df['Low'].map(f_zero2nan)
    df['Open'] = df['Open'].fillna(df['Close'])
    df['High'] = df['High'].fillna(df['Close'])
    df['Low'] = df['Low'].fillna(df['Close'])
    
    if adjust:
        adjust_price_value(df)
    if term>0:
        df = df.tail(term)
    return df

def normal_price(v0, v):
    if v==0 or v0==0:
        return True
    for price_limit in price_limit_table1:
        if price_limit.l<=v0 and v0<price_limit.h:
            if abs(v-v0)<=price_limit.w:
                return True
            else:
                return False
    for i in range(0, 5):
        a = pow(10, i)
        for price_limit in price_limit_table2:
            if price_limit.l*a<=v0 and v0<price_limit.h*a:
                if abs(v-v0)<=price_limit.w*a:
                    return True
                else:
                    return False
    if abs(v-v0)<=10000000:
        return True
    else:
        return False

def adjust_price_value(df):
    n = len(df)
    adjust_rate = 1.0
    v0 = df['Close'][n-1]
    for i in reversed(range(0, n-2)):
        v = df['Close'][i]
        if not normal_price(v0, v):
            next_adjust_rate = v0 / v
            if next_adjust_rate>=1.0:
                next_adjust_rate = int(Decimal(str(next_adjust_rate)).quantize(Decimal('0'), rounding=ROUND_HALF_EVEN))
            else:
                rev_next_adjust_rate = v / v0
                rev_next_adjust_rate = int(Decimal(str(rev_next_adjust_rate)).quantize(Decimal('0'), rounding=ROUND_HALF_EVEN))
                next_adjust_rate = 1.0/rev_next_adjust_rate
            adjust_rate = adjust_rate * next_adjust_rate
            #print('i={}, v0={}, v={} adjust={}'.format(i, v0, v, adjust_rate))
        v0 = v
        if adjust_rate!=1.0:
            df.iloc[i, 0] = int(df.Open[i]*adjust_rate)
            df.iloc[i, 1] = int(df.High[i]*adjust_rate)
            df.iloc[i, 2] = int(df.Low[i]*adjust_rate)
            df.iloc[i, 3] = int(df.Close[i]*adjust_rate)
            df.iloc[i, 4] = int(df.Volume[i]/adjust_rate)

