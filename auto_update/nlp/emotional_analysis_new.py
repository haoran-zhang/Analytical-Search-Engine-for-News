# -*- coding: utf-8 -*-
import os
import operator
import math

'''通过数情感词的词频来分析文章整体情感'''


def emotional_analysis(root_dir):
    """
    :param folder_path: xml3的路径，即分好词的文本的位置
    """

    # load dic
    senti_dic = {}

    with open(root_dir + '/nlp/senti_dic', 'r')as f:
        for line in f:
            lst = line.split()
            if len(lst) == 2:
                if lst[1] == '1':
                    senti_dic.setdefault(lst[0], 10)
                elif lst[1] == '0':
                    senti_dic.setdefault(lst[0], -10)
    with open(root_dir + '/nlp/merge_pos.txt', 'r')as f:
        for line in f:
            item = line.strip()
            if item not in senti_dic:
                senti_dic.setdefault(item, 1)
    with open(root_dir + '/nlp/merge_neg.txt', 'r')as f:
        for line in f:
            item = line.strip()
            if item not in senti_dic:
                senti_dic.setdefault(item, -1)

    # 切换到工作目录
    folder_path = root_dir + '/temp/xml_pages3'

    os.chdir(folder_path)
    f_lst = os.listdir(os.getcwd())
    f_lst.sort()

    # 统计全部文本中出现的词的词频
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

    f_result = open(root_dir + '/temp/senti', 'w')

    for f_item in f_lst:
        try:
            passage_length = 0
            f = open(f_item, 'r')
            feature_lst = []

            single_cnt = 0
            single_dic = {}
            for line in f:
                # 对每一个文本，也需要统计每个词的词频
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
                if 1.0 * value / single_cnt > 1.2 * total_dic[key] / total_cnt:  # 当一个词在该文本中的词频高于平均值1.2倍时，这个词就被视为特征词
                    feature_lst.append(key)

            neg_list = []   # 负极性词列表
            pos_list = []
            neg_num = []    # 负极性词对应的权值（手写字典权值是-10,其余为-1）
            pos_num = []

            score = 0
            for item in feature_lst:
                if item in senti_dic:
                    num = int(senti_dic[item])
                    score += num
                    if num > 0:
                        pos_list.append(item)
                        pos_num.append(str(senti_dic[item]))
                    elif num < 0:
                        neg_list.append(item)
                        neg_num.append(str(senti_dic[item]))

            # DEBUG 模式
            # print('\nPOS WORD',passage_length,'   ',f_item)
            # print(' '.join(pos_list))
            # print(' '.join(pos_num))
            # print('------------------------------------------------------')
            # print('NEG WORD')
            # print(' '.join(neg_list))
            # print(' '.join(neg_num))
            # print('\n')

            # 这样计算使分数受文章长度影响小、保持在-1到1之间、在0附近斜率大过度快、情感为负的文本数与情感为正文本比例越8：2
            s1 = f_item + ' ' + str(len(pos_list)) + '  ' + str(len(neg_list)) + '       %.2f' % (
                math.tanh(0.2 * (len(pos_list) + 2 * len(neg_list)) ** 2 * (score - 0.1 * len(feature_lst)) / len(
                    feature_lst) ** 2)) + '\n'

            f_result.write(s1)
            # DEBUG 模式
            # f_result.write(f_item + ' ' + str(len(pos_list)) + '  ' + str(len(neg_list)) + '       %.2f'
            #                % (math.tanh(5.0 * (score - 40) / len(feature_lst))) + '       %d     %.2f'
            #                % (passage_length, 100 * (len(pos_list) + len(neg_list)) / len(feature_lst)) + '\n')
        except Exception as e:
            print('Errors at emotional_analysis', e)
