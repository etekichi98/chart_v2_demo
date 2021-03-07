# -*- coding: utf-8 -*-
"""
Created on Sat Dec 12 11:15:54 2020
テクニカル分析の計算

@author: kurihara
"""

import pandas as pd
import math

def calc_todays_gc(shorts, longs):
    if len(shorts)<75:
        return False
    today = len(shorts) - 1
    yesterday = len(shorts) - 2
    short0 = shorts[yesterday]
    long0 = longs[yesterday]
    short = shorts[today]
    long = longs[today]
    if not math.isnan(short0) and not math.isnan(long0) and not math.isnan(short) and not math.isnan(long):
        if (short0-long0)<0 and (short-long)>0:
            return True
    return False

def calc_gc(shorts, longs):
    # ゴールデンクロス検出
    gcs = []
    short0 = shorts[0]
    long0 = longs[0]
    for i in range(len(shorts)):
        short = shorts[i]
        long = longs[i]
        if not math.isnan(short0) and not math.isnan(long0) and not math.isnan(short) and not math.isnan(long):
            if (short0-long0)<0 and (short-long)>0:
                gcs.append(shorts.index[i])
        short0 = short
        long0 = long
    return gcs

def calc_mav(df, s, m, l):
    # 移動平均
    mav = pd.DataFrame()
    mav["mav_s"] = df["Close"].rolling(s).mean()
    mav["mav_m"] = df["Close"].rolling(m).mean()
    mav["mav_l"] = df["Close"].rolling(l).mean()
    return mav

def calc_macd_accuracy(macd):
    gc1 = calc_gc(macd['macd'], macd['signal'])
    gc2 = calc_gc(macd['signal'], macd['macd'])
    gc1.extend(gc2)
    gc = sorted(gc1)
    if len(gc)>=2:
        term = gc[len(gc)-1] - gc[len(gc)-2]
        return term.days
    return 0

def calc_macd_accuracy2(macd, idx):
    gc1 = calc_gc(macd['macd'][:idx], macd['signal'][:idx])
    gc2 = calc_gc(macd['signal'][:idx], macd['macd'][:idx])
    gc1.extend(gc2)
    gc = sorted(gc1)
    if len(gc)>=2:
        term = gc[len(gc)-1] - gc[len(gc)-2]
        return term.days
    return 0
   
def calc_macd(df, es, el, sg):
    macd = pd.DataFrame()
    macd['ema_s'] = df['Close'].ewm(span=es).mean()
    macd['ema_l'] = df['Close'].ewm(span=el).mean()
    macd['macd'] = macd['ema_s'] - macd['ema_l']
    macd['signal'] = macd['macd'].ewm(span=sg).mean()
    macd['diff'] = macd['macd'] - macd['signal']
    f_plus = lambda x: x if x > 0 else 0
    f_minus = lambda x: x if x < 0 else 0
    macd['diff+'] = macd['diff'].map(f_plus)
    macd['diff-'] = macd['diff'].map(f_minus)
    return macd

def calc_stochastic(df, term):
    stochastic = pd.DataFrame()
    stochastic['%K'] = ((df['Close'] - df['Low'].rolling(term).min()) \
                        / (df['High'].rolling(term).max() - df['Low'].rolling(term).min())) * 100
    stochastic['%D'] = stochastic['%K'].rolling(3).mean()
    stochastic['%SD'] = stochastic['%D'].rolling(3).mean()
    stochastic['UL'] = 80
    stochastic['DL'] = 20
    return stochastic

def technical_analysis(df):
    mav = calc_mav(df, 5, 25, 75)
    stochastic = calc_stochastic(df, 14)
    macd = calc_macd(df, 12, 26, 9)
    return mav, stochastic, macd

def save_csv_file(out_path, df):
    mav, stochastic, macd = technical_analysis(df)
    with open(out_path,'w') as f:
        for i in range(len(df)):
            date_str = str(df.index[i])
            cv1 = df['Open'][i]
            cv2 = df['High'][i]
            cv3 = df['Low'][i]
            cv4 = df['Close'][i]
            cvc = df['Volume'][i]
            ma = macd['macd'][i]
            macd_diff = macd['diff'][i]
            line = '{}, {}, {}, {}, {}, {}, {}, {}\n'.format(date_str, cv1, cv2, cv3, cv4, cvc, ma, macd_diff)
            #line = date_str+','+cv1+','+cv2+','+cv3+','+cv4+','+cvc+','+str(macd_diff)+'\n'
            f.write(line)
