#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pickle
sent_dic={}
'''
这个文件是为了把sentiwordnet这个极性词典, 转化为实际使用的  {'abc':(pos_score, neg_score)...... } 字典

这个方法已经被淘汰
'''

def make_dic():
    f=open('/home/haoran/桌面/SentiWordNet_3.0.0_20130122.txt','r')
    cnt=0
    for line in f:
        lst=line.split()
        if len(lst)>4 and lst[2]=='0'  and lst[3]=='0':
            pass
        elif lst[0]=='#':
            pass
        else:
            print(lst)
            word=(lst[4])
            sent_dic.setdefault(word[:-2], (lst[2],lst[3]))
        cnt+=1
        # if cnt==1000:
        #     pass

    print(sent_dic)
    with open('/home/haoran/桌面/sent_dic','wb')as f2:
        pickle.dump(sent_dic,f2,protocol=2)
#
# #load dic
# with open('/home/haoran/桌面/sent_dic', 'rb')as f2:
#     sent_dic=pickle.load(f2)
#
# #caculate score
# f3=open('/home/haoran/桌面/0_trains.txt','r')
# pos_score=0
# neg_score=0
# for line in f3:
#     if line.strip() in sent_dic:
#         pos_score+=float(sent_dic[line.strip()][0])
#         neg_score+=float(sent_dic[line.strip()][1])
#
# print(pos_score,neg_score)
if '__name__'=='__main__':
    make_dic()