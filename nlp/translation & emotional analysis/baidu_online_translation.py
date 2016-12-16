# -*- coding: utf-8 -*-
import httplib
import md5
import urllib
import random
import pickle
import os

'''
这个文件用百度翻译api把分好的词翻译成英文，并用前100个文件的所有词得到一个字典, my_dic

使用python2

这个脚本后来也不用了，因为从中文翻译成英文、再查英文极性词典，能对应出来的极性词太少了
'''


def translate(input_q):
    appid = '20160718000025408'
    secretKey = '17YGuEKdDWP0YgAzxI0i'

    httpClient = None
    myurl = '/api/trans/vip/translate'
    q = input_q
    fromLang = 'zh'
    toLang = 'en'
    salt = random.randint(32768, 65536)

    sign = appid + q + str(salt) + secretKey
    m1 = md5.new()
    m1.update(sign)
    sign = m1.hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.quote(
        q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign

    httpClient = httplib.HTTPConnection('api.fanyi.baidu.com')
    httpClient.request('GET', myurl)
    try:
        # response是HTTPResponse对象
        response = httpClient.getresponse()
        s = response.read()
        left = 0
        right = 0
        for i in range(len(s) - 1, 0, -1):
            if s[i] == '"':
                if right == 0:
                    right = i
                else:
                    left = i
                    break
        return s[left + 1:right]
    except Exception as e:
        print(e)
    finally:
        if httpClient:
            httpClient.close()


os.chdir('/home/haoran/桌面/xml_pages3')
f_lst = os.listdir(os.getcwd())

# cnt_total=0
# cnt1=0
with open('/home/haoran/桌面/Extract_main_word&Sentiment_anaylsis/translation & emotional analysis/my_dic', 'rb') as f2:
    my_dict = pickle.load(f2)

for f_item in f_lst:
    f = open(f_item, 'r')

    for line in f:
        lst = line.split()
        if len(lst) == 2:
            try:
                if lst[0] not in my_dict:
                    rsp = translate(lst[0])
                    my_dict.setdefault(lst[0], rsp)
                else:
                    pass
            except:
                pass
        else:
            pass
    f.close()

with open('/home/haoran/桌面/Extract_main_word&Sentiment_anaylsis/translation & emotional analysis/my_dic', 'wb') as f3:
    pickle.dump(my_dict, f3)

f3.close()
# with open('/home/haoran/桌面/my_dic','rb')as f3:
#     my_dic=pickle.load(f3)
#
#
#
#
# #load dic
# with open('/home/haoran/桌面/sent_dic', 'rb')as f2:
#     sent_dic=pickle.load(f2)
#
# #caculate score
# os.chdir('/home/haoran/桌面/xml3/')
# f_lst = os.listdir(os.getcwd())
# f_result=open('/home/haoran/桌面/senti', 'w')
# for f_item in f_lst:
#     f=open(f_item,'r')
#     pos_score=0
#     neg_score=0
#     for line in f:
#         lst=line.split()
#         if len(lst)==2:
#             if lst[0] in my_dic:
#                 en_wrd=my_dic[lst[0]]
#                 if en_wrd in sent_dic:
#                     pos_score+=float(sent_dic[en_wrd][0])
#                     neg_score+=float(sent_dic[en_wrd][1])
#     f_result.write(f_item+' '+str(pos_score)+'  '+str(neg_score)+' '+str(pos_score-neg_score)+'\n')
