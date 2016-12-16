# -*- coding: utf-8 -*-
import mysql.connector
import os
'''这个文件是写fund2news这张表的，表中记录的是一个新闻的主元素是什么（某个行业、某个公司）'''


def fund2news(root_dir):
    os.chdir(root_dir + '/temp/xml_pages4/')
    f_list = os.listdir(os.getcwd())
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
    #
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
            # print(f_item,'---',fund,industry)
            cursor.execute("insert into fund2news (fund,industry,news_id) values (%s,%s,%s)", [fund, industry, f_item])
        except Exception as e:
            print("Exception as fund2news", e)

    conn.commit()
    conn.close()
