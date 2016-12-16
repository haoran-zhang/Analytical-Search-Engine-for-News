# -*- coding: utf-8 -*-
'''
这张表是把对文章详细的分析放入 news_info 这张表中，还是，数据文件还在本地
临时文件临时文件下个版本一定用临时文件
'''
import mysql.connector
import os
from bs4 import BeautifulSoup


def news_info(root_dir):
    os.chdir(root_dir + '/temp/xml_pages4/')
    f_list = os.listdir(os.getcwd())

    XML_FOLDER_PATH = root_dir + '/temp/xml_pages/'

    channels = {
        '贵金属': 0,
        '民航机场': 1,
        '电信运营': 2,
        '环保工程': 3,
        '酿酒行业': 4,
        '汽车行业': 5,
        '食品饮料': 6,
        '煤炭采选': 7,
        '家电行业': 8,
        '化肥行业': 9,
        '有色金属': 10,
        '造纸印刷': 11,
        '医药制造': 12,
        '医疗行业': 13,
        '珠宝首饰': 14,
        '安防设备': 15,
        '木业家具': 16,
        '公用事业': 17,
        '券商信托': 18,
        '化纤行业': 19,
        '仪器仪表': 20,
        '船舶制造': 21,
        '水泥建材': 22,
        '纺织服装': 23,
        '化工行业': 24,
        '塑胶制品': 25,
        '文化传媒': 26,
        '专用设备': 27,
        '商业百货': 28,
        '港口水运': 29,
        '房地产': 30,
        '软件服务': 31,
        '电子元件': 32,
        '机械行业': 33,
        '农牧饲渔': 34,
        '电子信息': 35,
        '交运物流': 36,
        '通讯行业': 37,
        '农药兽药': 38,
        '装修装饰': 39,
        '电力行业': 40,
        '工程建设': 41,
        '高速公路': 42,
        '金属制品': 43,
        '多元金融': 44,
        '输配电气': 45,
        '交运设备': 46,
        '文教休闲': 47,
        '材料行业': 48,
        '航天航空': 49,
        '钢铁行业': 50,
        '综合行业': 51,
        '玻璃陶瓷': 52,
        '国际贸易': 53,
        '石油行业': 54,
        '包装材料': 55,
        '银行': 56,
        '工艺商品': 57,
        '旅游酒店': 58,
        '保险': 59,
        '园林工程': 60}

    conn = mysql.connector.connect(user='chengxu', password='chengxu.gbh', database='nlp', host='127.0.0.1',
                                   port='3306')
    cursor = conn.cursor(buffered=True)
    senti_dic = {}
    with open(root_dir + '/temp/senti', 'r', encoding='utf-8') as senti:
        for line in senti:
            lst = line.split()
            if lst[-1] != '0':
                senti_dic.setdefault(lst[0], lst[-1])

    for f_item in f_list:
        try:
            cnt = 0
            fund = ''
            industry = ''
            with open(f_item, 'r', encoding='utf-8') as f:
                for line in f:
                    if cnt == 0:
                        lst = line.split()
                        if lst[1] == 'industry:':
                            industry_num = lst[-1].split('-')[-1]
                            for key, words in channels.items():
                                if words == int(industry_num):
                                    industry = key

                        elif lst[1] == 'company:':
                            fund = lst[2]
                            industry = ''
                    if cnt == 1:
                        lst = line.split()
                        if lst[1] == 'industry:':
                            industry_num = lst[-1].split('-')[-1]
                            for key, words in channels.items():
                                if words == industry_num:
                                    industry = key

                    cnt += 1
            keywords = line[12:]

            # 注释掉的部分是不写词频的关键词
            # lst2=line.split('  ')
            # lst3=[]
            # for item in lst2:
            #     item2=item.split(':')[0]
            #     if item2 != '' and item2[0]!='K':
            #         lst3.append(item2)
            #
            # keywords=','.join(lst3)



            # print(f_item,'---',fund,industry)

            with open(XML_FOLDER_PATH + f_item, encoding='utf-8') as f:
                data = f.read()
            soup = BeautifulSoup(data, 'lxml')
            title = ','.join(soup.title.text.split())

            url = 'http://fund.eastmoney.com/news/' + f_item + '.html'
            f_senti = senti_dic[f_item]
            time = f_item[5:13]
            # print(f_item,url,title,keywords,f_senti,fund,industry,time)

            cursor.execute(
                "insert into news_info (news_id,url,title,keywords,sentiment,main_character_fund,main_character_industry,time) values (%s,%s,%s,%s,%s,%s,%s,%s)",
                [f_item, url, title, keywords, f_senti, fund, industry, time])
        except Exception as e:
            print("Exception as news_to_mysql", e)
    conn.commit()
    conn.close()
