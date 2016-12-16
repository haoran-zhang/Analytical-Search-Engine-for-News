# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.shortcuts import render
from .forms import NameForm
from .mysql_con import mysql_con
from .mysql_con import es_search_api
import mysql.connector
import re
from collections import OrderedDict
import time
import pytz
from datetime import datetime

'''这个文件是网页的视图，链接了数据库和html输出的结果'''


# TODO:如果添加了新的源，应该添加这个字典，否则在网页中不会显示
source_dic = {'fund.eastmoney.com': '东方财富网', 'wallstreetcn.com': '华尔街见闻'}


def index(request):
    return render(request, 'search/index.html')


class Block:    # 这个类用于把数据库查询的结果包装一下整体传到html中
    def __init__(self, a, b, c, d, e, f, g, i='3'):
        self.title = a
        self.keyword = b
        self.senti = c
        self.update = d
        self.industry = e
        self.fund = f
        self.source = g
        self.image = i


def add_connect(fund, industry):
    """
    函数用于给一个公司找对应的行业
    """
    # print('fund : %s, industry : %s'%(fund,industry))
    if fund != '' and industry == '':
        conn = mysql.connector.connect(user='chengxu', password='chengxu.gbh', database='nlp', host='127.0.0.1',
                                       port='3306')
        cursor = conn.cursor()
        cursor.execute('select * from industry where company = %s', (fund,))

        values = cursor.fetchall()
        if values:
            values = values[0]
        if len(values) >= 2:
            return fund, values[1]
    else:
        return fund, industry


# def get_name(request):
#     '''
#     use mysql instead of elasticsearch to search
#     '''
#     if request.method == 'POST':
#         form = NameForm(request.POST)
#
#         if form.is_valid():
#             qurey=form.cleaned_data['entity']
#             mysql_ans=mysql_con(qurey)
#
#             if mysql_ans == []:  #检查404的情况
#                 ans={}
#                 ans.setdefault(qurey,0)
#                 return render(request,'search/not_found.html',{'ans':ans})
#
#             ans={}
#             for item in mysql_ans:
#                 key=item[1]
#                 # value =  OrderedDict()
#                 # value['标题: ' + item[2]]=18
#                 # value['抓取时间: ' + item[7]]=14
#                 # value['关键词: ' + item[3]]=14
#                 # value['情感值: ' + str(item[4])]=14
#                 # value['相关股票: ' + fund] = 14,
#                 # value['相关行业: ' + industry] = 14
#                 source=re.split(r'/+',key)[1]         #根据写好的词典来对应url的来源
#                 if source in source_dic:
#                     source=source_dic[source]
#
#                 fund, industry = add_connect(item[5], item[6])
#                 value=Block(item[2],item[3],item[4],item[7],industry,fund,source)
#                 ans[key]=value
#
#             return render(request, 'search/results.html', {'ans':ans})
#
#     else:
#         form = NameForm()
#
#     return render(request, 'search/results.html', {'form': form})


def check_if_code(query, signal=0):
    """
    查询是否输入的是股票代码
    input : signal是用户选择之后的返回结果，默认为0,选股票变为1,选基金变为2
    """
    additional_info = ''
    additional_info2 = ''
    hit_list = []
    hit_list2 = []

    if re.match('\d{6}', query):

        # 如果是6位数的代码，先查是否是股票代码
        conn = mysql.connector.connect(user='chengxu', password='chengxu.gbh', database='nlp', host='127.0.0.1',
                                       port='3306')
        cursor = conn.cursor()
        cursor.execute('select * from stock_code where stock_code = %s', (query,))
        values = cursor.fetchall()

        if values:
            query_new = values[0][1]  # return stock name
            ans_dict = es_search_api(query_new)  # 于是在es中用股票名称查这些新闻
            hit_list = ans_dict['hits']['hits']
            additional_info = query + ' : ' + query_new  # 这个变量是要返回股票名等多一点的信息

        # 再查是否是基金代码
        conn = mysql.connector.connect(user='chengxu', password='chengxu.gbh', database='nlp', host='127.0.0.1',
                                       port='3306')
        cursor = conn.cursor()
        cursor.execute('select * from fund where fund_id = %s', (query,))
        values2 = cursor.fetchall()
        if values2:
            query_lst = values2[0][-1].split(',')
            additional_info2 = query + ' : ' + values2[0][3] + ' : ' + ','.join(query_lst)  # 这个变量是要返回基金名、基金有哪些股票等多些的信息

            query_lst.insert(0, values2[0][3])

            hit_list2 = []
            for item in query_lst:
                ans_dict = es_search_api(item)  # 于是在es中用股票名称查这些新闻,一只基金包含的所有股票都查
                hit_list2 += ans_dict['hits']['hits']

        if values != [] and values2 == []:
            return hit_list, additional_info
        elif values2 != [] and values == []:
            return hit_list2, additional_info2
        elif values != [] and values2 != []:  # 如果代码既有对应的股票又有对应的基金
            if signal == 1:                  # 如果经过用户选择选了股票，signal是用户选择之后的返回结果，默认为0,选股票变为1,选基金变为2
                return hit_list, additional_info
            elif signal == 2:               # 如果选择了基金
                return hit_list2, additional_info2
            else:
                return hit_list, hit_list2, additional_info, additional_info2

        else:
            return [], ''

    else:    # 如果不是股票代码，就直接查query
        ans_dict = es_search_api(query)
        hit_list = ans_dict['hits']['hits']
        return hit_list, ''


def choose_es_get_name(request, para1):
    """
    这个函数仅在基金和股票的code重复的时候，用户通过点链接来确定是哪个，再返回结果
    :param para1:就是用户选择的结果，para1[-1]='1' 表示选的股票，para1[-1]='2' 表示选的基金
    :return:
    """
    additional_info = ''
    query = para1[:6]
    signal = int(para1[-1])  # 表示用户的选择是股票还是基金
    ans = check_if_code(query, signal)

    if len(ans) == 2:
        hit_list, additional_info = ans
        if additional_info != '':
            THRESHOLD = 1.0

    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)
    date = now.strftime('20%y%m%d')

    score_list = []
    score_list2 = []
    date_list = []
    for h_item in hit_list:
        pub_date = h_item['_source']['date']  # 这里体现了时效性！！
        delta = (
            datetime(int(date[:4]), int(date[4:6]), int(date[-2:])) - datetime(int(pub_date[:4]), int(pub_date[4:6]),
                                                                               int(pub_date[-2:]))).days  # 用来计算时间差
        date_list.append(delta)

        score_list.append(h_item['_score'] * max(0.4, 1 - 0.02 * delta))  # es搜索的结果乘上按时间衰减的权值，所以越新的新闻越容易被搜索出
        score_list2.append(h_item['_score'] * max(0.4, 1 - 0.02 * delta))

    score_list2.sort(reverse=True)
    for i in range(len(score_list2)):
        score_list2[i] = score_list.index(score_list2[i])

    if hit_list == [] or max(score_list) <= THRESHOLD:  # 如果都不是很相关，就输出404
        ans = {}
        if additional_info:
            ans.setdefault(additional_info, 0)
        else:
            ans.setdefault(query, 0)
        return render(request, 'search/not_found.html', {'ans': ans, 'q': query})

    ans = OrderedDict()
    for item in score_list2:
        if score_list[item] >= THRESHOLD:  # 过滤掉得分低的搜索结果
            key = hit_list[item]['_source']['url']
            source = re.split(r'/+', key)[1]  # 根据写好的词典来对应url的来源
            if source in source_dic:
                source = source_dic[source]

            fund, industry = add_connect(hit_list[item]['_source']['related_stock'],
                                         hit_list[item]['_source']['related_industry'])

            senti = hit_list[item]['_source']['senti']
            if senti > 0.5:             # 根据情感值选一个箭头的图片
                image = '1'
            elif senti > 0.15:
                image = '2'
            elif senti < -0.5:
                image = '5'
            elif senti < -0.15:
                image = '4'
            else:
                image = '3'

            value = Block(hit_list[item]['_source']['title'], hit_list[item]['_source']['keyword'],
                          hit_list[item]['_source']['senti'], hit_list[item]['_source']['date'], industry, fund, source,
                          image)   # 把搜索结果用Block类包装好
            ans[key] = value

            # show values in terminal
            print(item, hit_list[item]['_score'], hit_list[item]['_source']['title'])
    print('-------------------------------------------------------------')
    return render(request, 'search/results.html', {'ans': ans, 'add': additional_info, 'q': query})


def es_get_name(request):
    """
    用es搜索用户输入的query，与choose_es_get_name方法比较类似
    """
    THRESHOLD = 0.2  # 搜索结果的阈值
    additional_info = ''

    if request.method == 'POST':
        form = NameForm(request.POST)

        if form.is_valid():
            query = form.cleaned_data['entity']

            # ans_dict=es_search_api(query)
            # hit_list=ans_dict['hits']['hits']

            ans = check_if_code(query)
            if len(ans) == 2:
                hit_list, additional_info = ans
                if additional_info != '':
                    THRESHOLD = 1.0

            elif len(ans) == 4:
                hit_list, hit_list2, additional_info, additional_info2 = ans
                return render(request, 'search/stock_or_fund.html',
                              {'add': additional_info, 'add2': additional_info2, 'q': query})

            # 设置时区
            tz = pytz.timezone('Asia/Shanghai')
            now = datetime.now(tz)
            date = now.strftime('20%y%m%d')

            score_list = []
            score_list2 = []
            date_list = []
            for h_item in hit_list:
                pub_date = h_item['_source']['date']  # 这里体现了时效性！！
                delta = (datetime(int(date[:4]), int(date[4:6]), int(date[-2:])) - datetime(int(pub_date[:4]),
                                                                                            int(pub_date[4:6]),
                                                                                            int(pub_date[
                                                                                                -2:]))).days  # 用来计算时间差
                date_list.append(delta)

                score_list.append(h_item['_score'] * max(0.4, 1 - 0.02 * delta))  # es搜索的结果乘上按时间衰减的权值，所以越新的新闻越容易被搜索出
                score_list2.append(h_item['_score'] * max(0.4, 1 - 0.02 * delta))

            score_list2.sort(reverse=True)
            for i in range(len(score_list2)):
                score_list2[i] = score_list.index(score_list2[i])

            if hit_list == [] or max(score_list) <= THRESHOLD:  # 如果都不是很相关，就输出404
                ans = {}
                if additional_info:
                    ans.setdefault(additional_info, 0)
                else:
                    ans.setdefault(query, 0)
                return render(request, 'search/not_found.html', {'ans': ans, 'q': query})

            ans = OrderedDict()
            for item in score_list2:
                if score_list[item] >= THRESHOLD:  # 过滤掉得分低的搜索结果
                    key = hit_list[item]['_source']['url']
                    source = re.split(r'/+', key)[1]  # 根据写好的词典来对应url的来源
                    if source in source_dic:
                        source = source_dic[source]

                    fund, industry = add_connect(hit_list[item]['_source']['related_stock'],
                                                 hit_list[item]['_source']['related_industry'])

                    # SELECT A IMAGE ACCORDING TO SENTI_SCORE
                    senti = hit_list[item]['_source']['senti']
                    if senti > 0.5:   # 根据情感值选一个箭头的图片
                        image = '1'
                    elif senti > 0.15:
                        image = '2'
                    elif senti < -0.5:
                        image = '5'
                    elif senti < -0.15:
                        image = '4'
                    else:
                        image = '3'

                    value = Block(hit_list[item]['_source']['title'], hit_list[item]['_source']['keyword'],
                                  hit_list[item]['_source']['senti'], hit_list[item]['_source']['date'], industry, fund,
                                  source, image)   # 把搜索结果用Block类包装好
                    ans[key] = value

                    # show values in terminal
                    print(item, hit_list[item]['_score'], hit_list[item]['_source']['title'])
            print('-------------------------------------------------------------')

            return render(request, 'search/results.html', {'ans': ans, 'add': additional_info, 'q': query})

    else:
        pass
    ans = {}
    return render(request, 'search/results.html', {'ans': ans})
