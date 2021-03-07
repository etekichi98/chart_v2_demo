# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 14:23:57 2020

@author: kurihara
"""

import mplfinance as mpf
from muzinzo import technical_analysis as mzt

def calc_ylim(ser):
    max1 = ser.max()
    min1 = ser.min()
    if max1>0 and min1<0:
        max2 = max(max1, -min1)
        return max2, -max2
    elif max1>0 and min1>=0:
        return max1, 0
    else:
        return 0, min1
    
def generate_technical_addplot(df, f_volume, f_mav, f_stochastic, f_macd):
    panel_no = 0
    if f_volume: panel_no = panel_no + 1
    mav, stochastic, macd = mzt.technical_analysis(df)    
    mh, ml = calc_ylim(macd['macd'])
    sh, sl = calc_ylim(macd['signal'])
    apd_oscilator = []
    if f_stochastic:
        panel_no = panel_no + 1
        apd_oscilator.append(
            mpf.make_addplot((stochastic[['%D', '%SD', 'UL', 'DL']]),
                         ylim=[0, 100],
                         #ylabel='stocastics',
                         panel=panel_no))
    if f_macd:
        panel_no = panel_no + 1
        apd_oscilator.append(mpf.make_addplot((macd[['macd', 'signal']]),
                         ylim=[min(ml, sl), max(mh, sh)],
                         #ylabel='macd',
                         panel=panel_no))
        apd_oscilator.append(mpf.make_addplot((macd['diff+']), type='bar', color='r',
                         panel=panel_no))
        apd_oscilator.append(mpf.make_addplot((macd['diff-']), type='bar', color='b',
                         panel=panel_no))
    if f_mav and len(mav)>=75:
        apd_oscilator.append(mpf.make_addplot(mav[['mav_s', 'mav_m', 'mav_l']]))
    elif f_mav and len(mav)>=25:
        apd_oscilator.append(mpf.make_addplot(mav[['mav_s', 'mav_m']]))
    return apd_oscilator

def generate_technical_chart(title, df, volume=True, mav=True, 
                             stochastic=True, macd=True,
                             style='default', path=None):
    apd_oscilator = generate_technical_addplot(df, 
                    volume, mav, stochastic, macd)
    if path:
        mpf.plot(df, type='candle', volume=volume,
                 title=title, style=style,
                 ylabel='', ylabel_lower='',
                 addplot=apd_oscilator,
                 savefig=dict(fname=path,dpi=100))
    else:
        mpf.plot(df, type='candle', volume=volume,
                 title=title, style=style,
                 ylabel='', ylabel_lower='',
                 addplot=apd_oscilator)
        
def generate_simple_chart(title, df, volume=True, path=None):
    cs  = mpf.make_mpf_style(rc={"font.family":'IPAexGothic'})
    if path:
        mpf.plot(df, type='candle', volume=volume, title=title, style=cs,
                 mav=[5, 25, 75],
                 savefig=dict(fname=path,dpi=100))
    else:
        mpf.plot(df, type='candle', volume=volume, title=title, style=cs,
                 mav=[5, 25, 75])
