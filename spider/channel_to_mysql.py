# -*- coding: utf-8 -*-
from urllib import request
import pickle
'''这个脚本用来写channel这张表，记录了每个行业都有哪些公司（股票）'''

# conn=mysql.connector.connect(user='chengxu',password='chengxu.gbh',database='nlp',host='172.16.3.29',
#                              port='55009')
#
# cursor=conn.cursor(buffered=True)
# cursor.execute('select count(*) FROM news;')
#
channels = ['贵金属', '民航机场', '电信运营', '环保工程', '酿酒行业', '汽车行业', '食品饮料', '煤炭采选', '家电行业', '化肥行业',
            '有色金属', '造纸印刷', '医药制造', '医疗行业', '珠宝首饰', '安防设备', '木业家具', '公用事业', '券商信托', '化纤行业',
            '仪器仪表', '船舶制造', '水泥建材', '纺织服装', '化工行业', '塑胶制品', '文化传媒', '专用设备', '商业百货', '港口水运',
            '房地产', '软件服务', '电子元件', '机械行业', '农牧饲渔', '电子信息', '交运物流', '通讯行业', '农药兽药', '装修装饰', '电力行业',
            '工程建设', '高速公路', '金属制品', '多元金融', '输配电气', '交运设备', '文教休闲', '材料行业', '航天航空', '钢铁行业', '综合行业',
            '玻璃陶瓷', '国际贸易', '石油行业', '包装材料', '银行', '工艺商品', '旅游酒店', '保险', '园林工程']
# company_all_channel=pickle.load(open('C:/Users/i-zhanghaoran/Desktop/connection/all_company','rb'),encoding='utf-8')
# cnt=1
# for i in range(len(channels)):
#     for item in company_all_channel[i]:
#         cursor.execute("insert into industry (industry, company) values (%s,%s)",[channels[i], item])
#         cnt+=1
#
#
# conn.commit()
# conn.close()
channels2 = ['黄金', '白银', '铂金', '民航', '机场', '电信', '环保', '酿酒', '汽车', '食品', '煤炭', '家电', '化肥',
             '有色金属', '造纸', '医药', '医疗', '珠宝', '安防', '家具', '公用事业', '券商', '信托', '化纤',
             '仪器仪表', '船舶', '水泥建材', '纺织', '服装', '化工', '塑胶', '文化传媒', '专用设备', '百货', '港口',
             '房地产', '软件服务', '互联网', '电子元件', '机械', '农牧饲渔', '电子信息', '物流', '通讯', '农药', '装修', '电力',
             '工程', '高速公路', '金属', '金融', '输配电气', '交运设备', '文教休闲', '材料', '航天航空', '钢铁', '综合行业',
             '玻璃陶瓷', '国际贸易', '石油', '包装材料', '银行', '工艺', '旅游酒店', '保险', '园林']

cnt = 0
for item in channels:
    print('\'' + item + '\':' + str(cnt) + ',')
    cnt += 1

channel_dic = {
    '贵金属': 0,
    '黄金': 0,
    '白银': 0,
    '铂金': 0,
    '民航': 1,
    '电信': 2,
    '环保': 3,
    '酿酒': 4,
    '汽车': 5,
    '食品': 6,
    '煤炭': 7,
    '家电': 8,
    '化肥': 9,
    '有色金属': 10,
    '造纸': 11,
    '医药': 12,
    '医疗': 13,
    '珠宝': 14,
    '安防': 15,
    '家具': 16,
    '公用事业': 17,
    '券商': 18,
    '信托': 18,
    '化纤': 19,
    '仪器仪表': 20,
    '船舶': 21,
    '水泥': 22,
    '纺织服装': 23,
    '化工': 24,
    '塑胶': 25,
    '文化传媒': 26,
    '专用设备': 27,
    '百货': 28,
    '港口': 29,
    '房地产': 30,
    '软件': 31,
    '互联网': 31,
    '电子元件': 32,
    '机械': 33,
    '农牧饲渔': 34,
    '电子信息': 35,
    '物流': 36,
    '通讯': 37,
    '农药兽药': 38,
    '装修装饰': 39,
    '电力': 40,
    '工程建设': 41,
    '高速公路': 42,
    '金属制品': 43,
    '多元金融': 44,
    '输配电气': 45,
    '交运设备': 46,
    '文教休闲': 47,
    '材料行业': 48,
    '航天航空': 49,
    '钢铁': 50,
    '综合行业': 51,
    '玻璃陶瓷': 52,
    '国际贸易': 53,
    '石油': 54,
    '包装材料': 55,
    '银行': 56,
    '工艺商品': 57,
    '旅游酒店': 58,
    '保险': 59,
    '园林': 60
}

f2 = open('C:/Users/i-zhanghaoran/Desktop/connection/company_list', 'w', encoding='utf-8')
company_all_channel = pickle.load(open('C:/Users/i-zhanghaoran/Desktop/connection/all_company', 'rb'), encoding='utf-8')
for i in range(len(company_all_channel)):
    for j in range(len(company_all_channel[i])):
        f2.write(company_all_channel[i][j] + '\tCOMPANY_OF_INDUSTRY_' + str(i) + '\n')
for key, value in channel_dic.items():
    f2.write(key + '\tINDUSTRY-' + str(value) + '\n')

f2.close()
