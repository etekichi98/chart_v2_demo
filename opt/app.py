# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 18:11:08 2021

@author: kurihara
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import glob
import io
from flask import Flask, url_for, send_file, request, render_template
from flask_cors import CORS
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from muzinzo.Muzinzo import Muzinzo
import pandas as pd
#import mplfinance as mpf

#DATA_PATH = "\\\\larkbox\larkbox\muzinzo\data/"
#DATA_PATH = "/root/opt/share/data/"
DATA_PATH = "./data/"

app = Flask(__name__)
CORS(app)

mz = Muzinzo(DATA_PATH)

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

class ListFiles:
    def __init__(self, name, subject):
        self.name = name
        self.subject = subject

# http://サーバ:5000/?listfile=listfile.txt&watchfile=watchfile.txt
@app.route("/")
def index():
    arg_code = request.args.get('code', default=None, type=str)
    page_type = request.args.get('page_type', default='chart', type=str)
    style = request.args.get('style', default="default", type=str)
    term = request.args.get('term', default=120, type=int)
    stochastic = str2bool(request.args.get('stochastic', default="True", type=str))
    macd = str2bool(request.args.get('macd', default="True", type=str))

    llist_path = mz.get_database_path() + 'lists/*.txt'
    llist_files = sorted(glob.glob(llist_path))
    lfiles = []
    for llist_file in llist_files:
        filename = os.path.basename(llist_file)
        lf = ListFiles(filename, filename[:-4])
        lfiles.append(lf)

    wlist_path = mz.get_database_path() + 'watches/*.txt'
    wlist_files = sorted(glob.glob(wlist_path))
    wfiles = []
    for wlist_file in wlist_files:
        filename = os.path.basename(wlist_file)
        wf = ListFiles(filename, filename[:-4])
        wfiles.append(wf)

    lfile = request.args.get('listfile', default=None, type=str)
    wfile = request.args.get('watchfile', default=None, type=str)
    sl = []
    if not lfile and not wfile:
        # 全銘柄
        walk_around(sl)
    elif lfile and not wfile:
        list_path = mz.get_database_path() + 'lists/' + lfile
        df = pd.read_csv(list_path, header=None, names=['code','name'], encoding='UTF-8')
        for code in df['code']:
            s = StockList(code, mz.get_name(code))
            sl.append(s)
    elif not lfile and wfile:
        list_path = mz.get_database_path() + 'watches/' + wfile
        df = pd.read_csv(list_path, header=None, names=['code','name'], encoding='UTF-8')
        for code in df['code']:
            s = StockList(code, mz.get_name(code))
            sl.append(s)
    if arg_code==None or arg_code=='None':
        title = ''
    elif len(arg_code)==4 and int(arg_code)>1000:
        title = arg_code+' '+mz.get_name(int(arg_code))
    else:
        title = ''
    return render_template("index.html", title=title,
                           code=arg_code, page_type=page_type,
                           style=style, term=term,
                           stochastic=stochastic, macd=macd,
                           listfiles=lfiles, watches=wfiles,
                           selected=None, members=sl)

# http://サーバ:5000/help
@app.route('/help')
def help():
    return "Chart Server"

def make_title(code):
    if 1000<=code and code<=9999:
        title =str(code)+' '+mz.get_name(code)
    else:
        title = ''
    return title
    
    
# http://サーバ:5000/candle2?code=1001&term=200&volume=True
@app.route('/candle2')
def candle2():
    code = request.args.get('code', default=0, type=int)
    term = request.args.get('term', default=200, type=int)
    style = request.args.get('style', default="default", type=str)
    header_style = request.args.get('header_style', default="--home_menu_color:#4e71b0; --menu_color:#4e71b0; --title_color:#81ac28; --bg_color:#ffffff;", type=str)
    volume = request.args.get('volume', default="True", type=str)
    stochastic = str2bool(request.args.get('stochastic', default="True", type=str))
    macd = str2bool(request.args.get('macd', default="True", type=str))
    mav = str2bool(request.args.get('mav', default="True", type=str))

    title = make_title(code)
    return render_template("candle2.html", title=title,
                           code=code, term=term,
                           style=style, header_style=header_style,
                           volume=volume, stochastic=stochastic, 
                           macd=macd, mav=mav)

# http://サーバ:5000/candle?code=1001&term=200&volume=True
@app.route("/candle")
def candle():
    code = request.args.get('code', default=None, type=int)
    term = request.args.get('term', default=200, type=int)
    style = request.args.get('style', default="default", type=str)
    volume = str2bool(request.args.get('volume', default="True", type=str))
    stochastic = str2bool(request.args.get('stochastic', default="True", type=str))
    macd = str2bool(request.args.get('macd', default="True", type=str))
    mav = str2bool(request.args.get('mav', default="True", type=str))
    
    image = io.BytesIO()
    #style  = mpf.make_mpf_style(rc={"font.family":'IPAexGothic'})
    #style = 'yahoo'
    mz.plot_chart(code, term, title='', style=style, volume=volume,
                  stochastic=stochastic, macd=macd, mav=mav)
    plt.savefig(image, format='png')
    image.seek(0)
    return send_file(image, attachment_filename="image.png")

class StockTable:
    def __init__(self, date, open, high, low, close, volume):
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

# http://サーバ:5000/table?code=1001&term=200
@app.route("/table")
def table():
    code = request.args.get('code', default=None, type=int)
    term = request.args.get('term', default=40, type=int)
    header_style = request.args.get('header_style', default="--home_menu_color:#4e71b0; --menu_color:#4e71b0; --title_color:#81ac28; --bg_color:#ffffff;", type=str)
    
    title = make_title(code)
    df = mz.make_table(code, term)
    table = []
    for index, row in df.iterrows():
        t = StockTable(index.strftime('%Y/%m/%d'),
                       row['Open'],row['High'],row['Low'],row['Close'],row['Volume'])
        table.append(t)
    table.reverse()
    return render_template("table.html", title=title,
                           header_style=header_style,
                           code=code, term=term, table=table)


class StockList:
    def __init__(self, code, name):
        self.code = code
        self.name = name[:8]

def walk_around(sl):
    for i in range(1, 10):
        input_path = mz.get_database_path() + str(i*1000) + "/*.csv"
        csv_files = sorted(glob.glob(input_path))
        for csv_file in csv_files:
            filename = os.path.basename(csv_file)
            code = int(filename[0:4])
            s = StockList(code, mz.get_name(code))
            sl.append(s)
            
def str2bool(s):
     return s.lower() in ["true", "t", "yes", "y", "1"]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
