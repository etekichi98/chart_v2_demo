# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 14:55:40 2020

[無尽蔵]の過去の日足株価データから銘柄j辞書を作成する
http://www.mujinzou.jp/

@author: kurihara
"""

import glob

class Kdic:
    def __init__(self, name, market):
        self.name = name
        self.market = market

def create_dict():
    dict = {}
    return dict
           
def add_dict(dict, year):
    daily_files = glob.glob('./daily_data/{}/*.csv'.format(year))
    for daily_file in daily_files:
        with open(daily_file, mode='rb') as fd:
            lines = fd.readlines()
            for i, line in enumerate(lines):
                try:
                    line = line.decode('cp932')
                except:
                    print('error file {}: line {}'.format(daily_file, i))
                    # utf-8でないバイト列が含まれる行はスキップする
                    continue
                line = line.rstrip()
                line_list = line.split(',')
                if len(line_list)==10:
                    if len(line_list[1])==4:
                        name = line_list[3]
                        dict[line_list[1]] = Kdic(name[5:], line_list[9])
                else:
                    print('error file {}: line {} : {}'.format(daily_file, i, line))

def save_dict(dict, path):
    sorted_dict = sorted(dict.items(), key=lambda x:x[0])
    with open(path,'w', encoding='utf-8') as f:
        for krec in sorted_dict:
            line = krec[0]+','+krec[1].name+','+krec[1].market+'\n'
            f.write(line)
 
def load_dict(path):
    dict = {}
    with open(path, mode='r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            line = line.rstrip()
            line_list = line.split(',')
            dict[line_list[0]] = Kdic(line_list[1], line_list[2])
    return dict
    
def main():
    dict = create_dict()
    for year in range(2015, 2021):
        add_dict(dict, year)
    save_dict(dict, 'kdic.csv')
    #dict2 = load_dict('kdic.csv')
    #for krec in dict2:
    #    print(dict2[krec].name, dict2[krec].market)
    
if __name__ == '__main__':
    main()

