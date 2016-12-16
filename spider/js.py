# -*- coding: utf-8 -*-
from urllib import request
import pickle
'''
 这个文件导出每一个行业分类都有哪些股票,不常用
'''

TOKEN='7bc05d0d4c3c22ef9fca8c2a912d779c'

channels=['贵金属', '民航机场', '电信运营', '环保工程', '酿酒行业', '汽车行业', '食品饮料', '煤炭采选', '家电行业', '化肥行业',
          '有色金属', '造纸印刷', '医药制造', '医疗行业', '珠宝首饰', '安防设备', '木业家具', '公用事业', '券商信托', '化纤行业',
          '仪器仪表', '船舶制造', '水泥建材', '纺织服装', '化工行业', '塑胶制品', '文化传媒', '专用设备', '商业百货', '港口水运',
          '房地产', '软件服务', '电子元件', '机械行业', '农牧饲渔', '电子信息', '交运物流', '通讯行业', '农药兽药', '装修装饰', '电力行业',
          '工程建设', '高速公路', '金属制品', '多元金融', '输配电气', '交运设备', '文教休闲', '材料行业', '航天航空', '钢铁行业', '综合行业',
          '玻璃陶瓷', '国际贸易', '石油行业', '包装材料', '银行', '工艺商品', '旅游酒店', '保险', '园林工程']
company_all_channel=[]

url_list=l=[732,420,736,728,477,481,438,437,456,731,478,470,465,77,734,735,476,427,473,471,458,729,424,436,538,454,486,
            910,482,450,451,737,459,545,433,447,422,448,730,725,428,425,421,739,738,457,429,740,537,480,479,539,546,484,
            464,733,475,440,485,474,726]


def process(s):
    company_list=[]
    s=s[2:-2]
    left=-1
    right=-1
    for i in range(len(s)):
        if s[i]=='"'and left==-1:
            left=i
            continue
        if s[i]=='"' and left!=-1 and right ==-1 :
            right=i
            company=s[left+1:right]
            company_list.append(company.split(',')[2])
            left=-1
            right=-1
    return company_list


for idx in url_list:
    url='http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C.BK0'+str(idx)+'1&sty=FCOIATA&token='+TOKEN+'&'
    with request.urlopen(url)as f:
        data = f.read().decode('utf-8')
    company_all_channel.append(process(data))
    print(company_all_channel)

pickle.dump(company_all_channel,open('C:/Users/i-zhanghaoran/Desktop/connection/all_company','wb'))