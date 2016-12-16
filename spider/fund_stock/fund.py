# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urllib import request
from multiprocessing import Pool
import re
import time
import pickle

'''
这个程序可以爬到基金公司-基金-股票的关系，需要偶尔更新，比较重要
'''

TOKEN = '8a36403b92724d5d1dd36dc40534aec5'
ROOT_DIR = './content'   # 用起来的时候记得修改路径


def process(s):
    '''
    只是一个处理格式化字符串的小函数，之前的url会返回很多内容，只有名字有用
    '''
    company_list = []
    s = s[2:-2]
    left = -1
    right = -1
    for i in range(len(s)):
        if s[i] == '"' and left == -1:
            left = i
            continue
        if s[i] == '"' and left != -1 and right == -1:
            right = i
            company = s[left + 1:right]
            company_list.append(company.split(',')[2])
            left = -1
            right = -1
    return company_list


def fund(tp):
    '''
    针对一支基金，爬下来所有的股票名称
    :param tp: 包含url和基金公司名的元组，只有url有用
    :return: 一只基金重仓的top10只股票
    '''
    current_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    fund_code = tp[0]
    url = 'http://fund.eastmoney.com/pingzhongdata/' + fund_code + '.js?v=' + current_time
    stockCodes = []
    with request.urlopen(url) as f:
        data = f.read().decode('utf-8')
        data_list = data.split('\n')
        for item in data_list:
            if item[:14] == 'var stockCodes':
                # print(item.split('"')[1].split(','))
                stockCodes.append(item.split('"')[1].split(','))

    cmd = ','.join(stockCodes[0])
    url1 = 'http://nufm3.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=' + cmd + '&' \
                                                                                                  'sty=E1OQCPZT&token=' + TOKEN
    try:
        with request.urlopen(url1) as f:
            data1 = f.read().decode('utf-8')
            return process(data1)
    except Exception as e:
        print(e, 'function: fund', url1)
        # print('------------',process(data1))


def single_company(tp):
    '''
    这个是针对一家基金公司，爬下来所有的基金情况和基金经理名字。这里只选了股票型基金，具体的可以在下面改。
    :param tp: 是一个(url, 基金公司名)的元组
    '''
    fund_manager = []
    url = tp[0]
    with request.urlopen(url) as f:
        data = f.read()
        # print(data.decode('gb2312'))
    soup2 = BeautifulSoup(data, 'lxml')
    a_lst = soup2.find_all('a')
    cnt = 0
    for link in a_lst:
        if 'href' in link.attrs and re.match(r'http://fund.eastmoney.com/\d{6}.html', link['href']):
            num = link['href'][-11:-5]
            cnt += 1
            for parent in link.parents:
                if parent.name == 'table' and 'id' in parent.attrs and parent['id'] == 'tb_1_0':  # 这个条件是为了选出股票基金
                    for link2 in a_lst:
                        if 'href' in link2.attrs and re.match(r'http://fund.eastmoney.com/f10/jjjl_' + num + '.html',
                                                              link2['href']):
                            fund_manager.append((num, link.text, link2.text))
    fund_manager = list(set(fund_manager))
    ans = []
    for item in fund_manager:
        try:
            ans.append((item, fund(item)))
        except Exception as e:
            print(e, item, ' function: signle_company')
    # print(ans,'------------------')
    return ans


def company_list(item, f_num, root_dir='.'):
    '''
    input 输入一个人元组和文件名。元组包含一家基金公司页面的url和这家公司名
    :param ： tridim_table:记录了这家公司包含哪些基金、每个基金又有哪些股票
    '''
    tridim_table = []
    try:
        tridim_table.append((item[1], single_company(item)))
    except Exception as e:
        print('Exception is ', e, item, ' function: company_list')
    pickle.dump(tridim_table, open(root_dir + '/tridim_table' + str(f_num), 'wb'))


def main(root_dir='.'):
    '''
    main_content 是基金公司页面的地址。一共116家公司，我用了32个进程并行，布置的时候再看情况调整
    '''
    main_content = 'http://fund.eastmoney.com/company/default.html'
    sub_url = []
    with request.urlopen(main_content)as f:
        data = f.read()
    soup = BeautifulSoup(data.decode('gb2312'), 'lxml')
    for link in soup.find_all('a'):
        if 'href' in link.attrs and re.match(r'http://fund.eastmoney.com/company/\d{8}.html', link['href']):
            sub_url.append((link['href'], link.text))
    # print((link['href'], link.text))
    p = Pool(32)

    for i in range(len(sub_url)):
        p.apply_async(company_list, args=(sub_url[i], i, root_dir))
    p.close()
    p.join()
    print('ALL DONE')


# ans=single_company(('http://fund.eastmoney.com/company/80163340.html', '安信'))
# print(ans,len(ans))
# print(fund(('002029', '蓝雁书')))
main(ROOT_DIR)
