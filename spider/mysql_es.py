# -*- coding: utf-8 -*-
import mysql.connector
import pickle
import pycurl
from io import BytesIO
import json
import os

'''
这个程序比较重要，是从mysql下载数据再导入es中
初始的时候需要create mapping，之后只用一条一条插就好了
'''


class Es:
    def __init__(self, path):  # 用项目路径来初始化
        self.root_dir = path
        self.values = []
        self.news = []

    def download_from_mysql(self):
        """
        根据xml——pages的文件名下载news和news—info两张表的数据
        """
        os.chdir(self.root_dir + '/temp/xml_pages')
        f_lst = os.listdir(os.getcwd())
        values = []
        values2 = []

        conn = mysql.connector.connect(user='chengxu', password='chengxu.gbh', database='nlp', host='127.0.0.1',
                                       port='3306')
        cursor = conn.cursor(buffered=True)
        for item in f_lst:
            url = 'http://fund.eastmoney.com/news/' + item + '.html'
            cursor.execute("select * from news_info where url = %s", (url,))
            values += cursor.fetchall()

        conn.close()
        pickle.dump(values, open(self.root_dir + '/temp/news_info', 'wb'))

        conn2 = mysql.connector.connect(user='chengxu', password='chengxu.gbh', database='nlp', host='127.0.0.1',
                                        port='3306')
        cursor2 = conn2.cursor(buffered=True)

        for item in f_lst:
            url = 'http://fund.eastmoney.com/news/' + item + '.html'
            cursor2.execute("select * from news where url = %s", (url,))
            values2 += cursor2.fetchall()

        conn2.close()
        pickle.dump(values2, open(self.root_dir + '/temp/news', 'wb'))

    def load(self):
        """
        把两个临时文件读入类的变量中，再清空两个文件
        """
        self.values = pickle.load(open(self.root_dir + '/temp/news_info', 'rb'))
        self.news = pickle.load(open(self.root_dir + '/temp/news', 'rb'))
        f = open(self.root_dir + '/temp/news_info', 'w')
        f1 = open(self.root_dir + '/temp/news', 'w')
        f.write('')
        f1.write('')

    def create_mapping(self):
        """
        只在新建一个es的index才用的到
        """
        # 新建index
        c = pycurl.Curl()
        c.setopt(pycurl.URL, 'http://localhost:9200/nlp')
        c.perform()
        c.close()

        # 创建一个map，用到了ik这个分词库
        data = {
            "news_info": {
                "_all": {
                    "analyzer": "ik_smart",
                    "search_analyzer": "ik_smart",
                },
                "properties": {
                    "title": {
                        "type": "string",
                        "analyzer": "ik_smart",
                        "search_analyzer": "ik_smart",
                        "index": "analyzed",
                        "boost": 15
                    },
                    "keyword": {
                        "type": "string",
                        "analyzer": "ik_smart",
                        "search_analyzer": "ik_smart",
                        "index": "analyzed",
                        "boost": 10
                    },
                    "text": {
                        "type": "string",
                        "analyzer": "ik_smart",
                        "index": "analyzed",
                        "search_analyzer": "ik_smart",
                        "boost": 3
                    },
                    "related_stock": {
                        "type": "string",
                        "analyzer": "ik_smart",
                        "index": "analyzed",
                        "search_analyzer": "ik_smart",
                        "boost": 12
                    },
                    "related_fund": {
                        "type": "string",
                        "analyzer": "ik_smart",
                        "index": "analyzed",
                        "search_analyzer": "ik_smart",
                        "boost": 12
                    },
                    "date": {"type": "string"}
                }
            }
        }

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL, 'http://localhost:9200/nlp/news_info/_mapping')
        c.setopt(pycurl.CUSTOMREQUEST, "POST")
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, '%s' % json.dumps(data))
        c.setopt(pycurl.WRITEFUNCTION, buffer.write)
        c.perform()
        c.close()

        body = buffer.getvalue()
        print(body.decode('utf-8'))

    def create_item(self, db_item):
        """
        creat a item in elasticsearch /nlp/news_info/...
        :param db_item: DATA FORM: ID, URL, TITLE, KEYWORD, SENTI_SCORE, RELATED_STOCK, RELATED INDUSTRY, DATE
        """
        text = ''
        id = db_item[0]
        url = db_item[1]
        for item in self.news:
            if item[3] == url:
                text = item[6]

        data = {'url': db_item[1], 'title': db_item[2], 'keyword': db_item[3], 'senti': db_item[4],
                'related_stock': db_item[5], 'related_industry': db_item[6], 'date': db_item[7], 'text': text}

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL, 'http://localhost:9200/nlp/news_info/{}?pretty'.format(id))

        c.setopt(pycurl.CUSTOMREQUEST, "PUT")
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, '%s' % json.dumps(data))

        c.setopt(pycurl.WRITEFUNCTION, buffer.write)
        c.perform()
        c.close()

        body = buffer.getvalue()
        # print(body.decode('utf-8'))

    def main(self):
        self.download_from_mysql()
        self.load()
        for item in self.values:
            try:
                self.create_item(item)
            except Exception as e:
                print('Exceptions occur at mysql_es', e)
