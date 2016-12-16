# -*- coding: utf-8 -*-
import mysql.connector
import os
from bs4 import BeautifulSoup

'''这个程序经过简单分析的文本,写入news这张表'''


def news(root_dir):
    conn = mysql.connector.connect(user='chengxu', password='chengxu.gbh', database='nlp', host='127.0.0.1',
                                   port='3306')
    cursor = conn.cursor(buffered=True)
    cursor.execute('select count(*) FROM news;')

    cnt = 0
    path = root_dir + '/temp/xml_pages'
    os.chdir(path)
    f_lst = os.listdir(os.getcwd())
    for item in f_lst:
        try:
            url = 'http://fund.eastmoney.com/news/' + item + '.html'
            with open(item, 'rb') as f:
                soup = BeautifulSoup((f.read()).decode('utf-8'), 'lxml')
                cnt += 1
                site = 'fund.eastmoney.com'
                title = ','.join(str(soup.title.text).split())
                # print(soup.description)
                meta = str(soup.description.text)
                desc = str(soup.desc.text).strip().split('\n')
                for item_w in desc:
                    if '>>' in item_w or '【' in item_w:
                        desc.remove(item_w)
                desc = ''.join(desc[:-1])
                desc = ''.join(desc.split())

                i = 0
                length = len(desc)
                while i < length:
                    if desc[i] in ['‘', '’', '“', '”', '\n', '。', '，', '！', '？', '、', '；', '【', '】', '(', ')']:
                        # print(desc[i-1],desc[i])
                        desc = desc[:i] + '\\' + desc[i:]
                        length += 1
                        i += 1
                    i += 1

                desc = desc.encode('utf-8').decode('utf-8')

                keyword = str(soup.keyword.text)
                # print(desc)
                # print(url,'------------\n',id,'------------\n',site,'------------\n',title,'------------\n',meta,'------------\n',keyword,'\n\n')
                cursor.execute("insert into news ( site, title,url, keyword, meta, `desc`) values (%s,%s,%s,%s,%s,%s)",
                               [site, title, url, keyword, meta, desc])
                # cursor.execute('insert into news ( url, `desc`) values (%s,%s)', [url, desc])  #what!!!! 注意这个地方。。。

        except Exception as e:
            print('error occures as ', item, e)

    conn.commit()
    conn.close()
