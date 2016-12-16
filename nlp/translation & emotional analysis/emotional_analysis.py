# -*- coding: utf-8 -*-
import os
import pickle
import operator

'''
这个文件是用两个词典（中英词典，情感词典）来对分好词的文件做极性分析

这个脚本是使用之前的方法，就是中文翻译成英文在查字典，已经被淘汰，换用emotional_analysis_new.py
'''


def emotional_analysis(folder_path, result_path='senti'):
    '''
    :param folder_path: xml3的路径，即分好词的文本文件位置  result_path： 是输出情感分析结合的文件
    :return:
    '''
    sent_dic = {}
    my_dic = {}

    # load dic
    with open('sent_dic', 'rb')as f2:
        sent_dic = pickle.load(f2)
    with open('my_dic', 'rb')as f3:
        my_dic = pickle.load(f3)

    # caculate score
    os.chdir(folder_path)
    f_lst = os.listdir(os.getcwd())
    f_lst.sort()

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
    #                     print(lst[0].decode('utf-8'))
    #                     print(sent_dic[en_wrd][0],sent_dic[en_wrd][1])
    #                     pos_score+=float(sent_dic[en_wrd][0])
    #                     neg_score+=float(sent_dic[en_wrd][1])
    #
    #     num = pos_score - neg_score - 14
    #     if num>=5:s='+'
    #     elif num<=5-4:s='-'
    #     else:s='0'
    #     f_result.write(f_item+' '+str(pos_score)+'  '+str(neg_score)+'      '+s+'\n')
    #

    # COUNT TOTAL WORD FREQUENCY!
    total_cnt = 0
    total_dic = {}
    for f_item in f_lst:
        f = open(f_item, 'r')
        for line in f:
            total_cnt += 1
            lst = line.split()
            if len(lst) == 2:
                if lst[0] not in total_dic and (lst[1] != 'ude1' and lst[1][0] != 'w'):
                    total_dic.setdefault(lst[0], 1)
                elif lst[1] != 'ude1' and lst[1][0] != 'w':
                    total_dic[lst[0]] += 1
        f.close()

    # sorted_total_dic = sorted(total_dic.items(), key=operator.itemgetter(1), reverse=True)
    # for key, value in sorted_total_dic:
    #     print key.decode('utf-8'),value


    # COUNT SINGLE FILE FREQUENCY
    f_result = open(result_path, 'w')

    for f_item in f_lst:
        passage_length = 0
        f = open(f_item, 'r')
        feature_lst = []
        pos_score = 0
        neg_score = 0

        single_cnt = 0
        single_dic = {}
        for line in f:
            passage_length += 1
            single_cnt += 1
            lst = line.split()
            if len(lst) == 2:
                if lst[0] not in single_dic and (lst[1] != 'ude1' and lst[1][0] != 'w'):
                    single_dic.setdefault(lst[0], 1)
                elif lst[1] != 'ude1' and lst[1][0] != 'w':
                    single_dic[lst[0]] += 1
        sorted_single_dic = sorted(single_dic.items(), key=operator.itemgetter(1), reverse=True)
        for key, value in sorted_single_dic:
            if 1.0 * value / single_cnt > 1.2 * total_dic[key] / total_cnt:
                feature_lst.append(key)

        # for item in feature_lst:
        #     print(item.decode('utf-8'))
        # TODO DELETE THIS AFTER DEBUG
        neg_list = []
        pos_list = []
        neg_num = []
        pos_num = []

        f.seek(0)
        for line in f:
            lst = line.split()
            if len(lst) == 2:
                if lst[0] in my_dic:
                    en_wrd = my_dic[lst[0]]
                    if en_wrd in sent_dic:
                        # print(lst[0].decode('utf-8'))
                        # print(sent_dic[en_wrd][0],sent_dic[en_wrd][1])
                        pos_score += float(sent_dic[en_wrd][0])
                        neg_score += float(sent_dic[en_wrd][1])

                        if float(sent_dic[en_wrd][1]) - float(sent_dic[en_wrd][0]) > 0.1:
                            neg_list.append(lst[0])
                            neg_num.append('%.3f' % (float(sent_dic[en_wrd][1]) - float(sent_dic[en_wrd][0])))
                        if float(sent_dic[en_wrd][0]) - float(sent_dic[en_wrd][1]) > 0.1:
                            pos_list.append(lst[0])
                            pos_num.append('%.3f' % (float(sent_dic[en_wrd][0]) - float(sent_dic[en_wrd][1])))

        print('\nPOS WORD', passage_length)
        print(' '.join(pos_list))
        print(' '.join(pos_num))
        print('------------------------------------------------------')
        print('NEG WORD')
        print(' '.join(neg_list))
        print(' '.join(neg_num))
        print('\n')

        num = 5000.0 * pos_score / passage_length - 5000.0 * neg_score / passage_length

        if pos_score + neg_score == 0:
            s = '0'
        elif num >= 0:
            s = '%.6s' % (num / (5000.0 * pos_score / passage_length + 5000.0 * neg_score / passage_length))
        elif num < 0:
            s = '%.6s' % (num / (5000.0 * pos_score / passage_length + 5000.0 * neg_score / passage_length))

        f_result.write(f_item + ' ' + str(pos_score) + '  ' + str(neg_score) + '      ' + s + '\n')


emotional_analysis('/home/haoran/桌面/xml_test')
