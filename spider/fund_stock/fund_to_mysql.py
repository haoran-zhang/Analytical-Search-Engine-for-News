# -*- coding: utf-8 -*-
from urllib import request
import pickle
import mysql.connector
import os

'''把基金信息导入mysql，包括一支基金都有哪些股票'''
ROOT_DIR = './content/'

os.chdir(ROOT_DIR)
f_list = os.listdir(os.getcwd())

conn = mysql.connector.connect(user='chengxu', password='chengxu.gbh', database='nlp', host='172.16.3.29',
                               port='55009')
cursor = conn.cursor(buffered=True)

for f_item in f_list:
    tridim_table = pickle.load(open(f_item, 'rb'), encoding='utf-8')
    cnt = 1
    com = str(tridim_table[0][0])
    lst = tridim_table[0][1]
    # cursor.execute("insert into industry (industry, company) values (%s,%s)",[channels[i], item])
    print(lst, len(lst))
    for i in range(len(lst)):
        fund = lst[i][0]
        try:
            stock = ','.join(lst[i][1])
        except:
            stock = str(lst[i][1])
        fund_id = fund[0]
        fund_name = fund[1]
        fund_manager = fund[2]
        # print('fund: '+fund_code+' '+fund_name+' '+fund_manager)
        # print('stock '+','.join(stock))
        cursor.execute("insert into fund (fund_company,fund_id,fund_name,fund_manager,stock) values (%s,%s,%s,%s,%s)",
                       [com, fund_id, fund_name, fund_manager, stock])

conn.commit()
conn.close()
