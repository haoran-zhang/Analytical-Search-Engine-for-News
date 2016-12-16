# -*- coding: utf-8 -*-
import mysql.connector
import os
import pycurl
from io import BytesIO
import json


def mysql_con(qurey):
    """
    这个函数用来从mysql里面查询相关文章的条目
    :param qurey: 查询字符串，表示行业或者公司
    :return: 返回的是相关文章列表
    """
    conn = mysql.connector.connect(user='chengxu', password='chengxu.gbh', database='nlp', host='127.0.0.1',
                                   port='3306')
    cursor = conn.cursor()
    cursor.execute('select * from fund2news where fund = %s', (qurey,))
    values = cursor.fetchall()
    cursor.execute('select * from fund2news where industry = %s', (qurey,))
    values2 = cursor.fetchall()
    ans = []
    # print(values+values2)
    for item in values + values2:
        if item != '':
            cursor.execute('select * from news_info where news_id = %s', (item[3],))
            ans += cursor.fetchall()

    cursor.close()
    conn.close()
    return ans


def es_search_api(query):
    """
    这个函数用来从mysql里面查询相关文章的条目
    :param qurey: 查询字符串，表示行业或者公司
    :return: 返回的是相关文章列表
    """
    #
    # data = {
    #     "query": {
    #         "bool": {
    #             "should": [
    #                 {"match": {"title": "{}".format(query)}},
    #                 {"match": {"text": "{}".format(query)}},
    #                 {"match": {"keyword": "{}".format(query)}},
    #                 {"match": {"related_stock": "{}".format(query)}},
    #                 {"match": {"related_industry": "{}".format(query)}},
    #             ]
    #         }
    #     }
    # }

    # 这里es同时用了两种搜索语句。这两种搜索结果不太一样，第一种是尽可能在一篇文章的不同位置都出现，
    # 这样搜索出的结果与主题更相关;第二种是只要出现就行，因此能找到非常偏的词如“脱欧”。试用后决定两种平均一下效果最好
    data = {
        "query": {
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": "{}".format(query),
                            "fields": [
                                "title",
                                "keyword",
                                "text",
                                "related_stock",
                                "related_fund"
                            ]
                        }
                    },
                    {"match": {"title": "{}".format(query)}},
                    {"match": {"text": "{}".format(query)}},
                    {"match": {"keyword": "{}".format(query)}},
                    {"match": {"related_stock": "{}".format(query)}},
                    {"match": {"related_industry": "{}".format(query)}}
                ]
            }
        }
    }

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(pycurl.URL, 'http://localhost:9200/nlp/news_info/_search?pretty')
    c.setopt(pycurl.CUSTOMREQUEST, "POST")
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, '%s' % json.dumps(data))
    c.setopt(pycurl.WRITEFUNCTION, buffer.write)
    c.perform()
    c.close()

    body = buffer.getvalue()
    s = body.decode('utf-8')

    f = open('./temp', 'w')
    f.write(s)
    f.close()

    d = json.load(open('./temp', 'r'))
    return d
