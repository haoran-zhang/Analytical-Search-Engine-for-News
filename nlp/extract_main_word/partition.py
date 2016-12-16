#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
这个文件是调用nlpir和自己写的字典, bigdic.txt来做分词和关键词提取
这个脚本已经被partition_main_character 替代了，因为那个文件新增了主元素提取的功能
'''
import pynlpir
import ctypes
import os
import tempfile
import pickle


def load_fund_table(folder_path):
    stock_fund = []
    os.chdir(folder_path)
    f_list = os.listdir(os.getcwd())
    for f_item in f_list:
        tridim_table = pickle.load(open(f_item, 'rb'), encoding='utf-8')
        cnt = 1
        com = str(tridim_table[0][0])
        lst = tridim_table[0][1]
        for i in range(len(lst)):
            fund = lst[i][0]
            try:
                stock = ' '.join(lst[i][1])
            except:
                stock = str(lst[i][1])
            fund_id = fund[0]
            fund_name = fund[1]
            fund_manager = fund[2]
            stock_fund.append((fund_name, lst[i][1]))
    return stock_fund


def stock2fund(ans_set, feqrence, l):
    related_fund = []
    s = ''
    s += ' (' + str(ans_set[l][1]) + ': ' + str(feqrence[l]) + ')'
    if ans_set[l][0][:7] == 'COMPANY':
        stock_name = ans_set[l][1]
        for i in range(len(stock_fund)):
            if stock_fund[i][1] and stock_name in stock_fund[i][1]:
                related_fund.append(stock_fund[i][0])
        s += '\nRelated_fund: ' + ','.join(related_fund)
        s += '\n'
    return s


def partition(input_path, output_path):
    '''
    分词，把input _path 里的文本文件分词，结果存在output_path
    :param input_path: 文本文件路径
    :param output_path: 分词结果的路径
    :return: 编码错误的词的错误
    '''
    f3 = tempfile.NamedTemporaryFile(mode='w+t', encoding='utf-8')
    f3_name = f3.name

    stop_set = []
    f_stop_list = open(
        'C:/Users/i-zhanghaoran/Desktop/Extract_main_word&Sentiment_anaylsis/extract_main_word/stop_list.txt', 'r',
        encoding='utf-8')
    for line in f_stop_list:
        stop_set.append(line.split()[0])
    stop_set = set(stop_set)

    os.chdir(input_path)
    f_lst = os.listdir(os.getcwd())
    cnt1 = 0
    nlpir = pynlpir.nlpir
    pynlpir.open()
    nlpir.ImportUserDict(b'C:/Users/i-zhanghaoran/Desktop/Extract_main_word&Sentiment_anaylsis/new_bigdic.txt')
    for item in f_lst:
        ans_lst = []
        f = open(item, 'r', encoding='utf-8')
        s = bytes(f.read(), encoding='utf-8')
        f.close()

        size = ctypes.c_int()
        result = nlpir.ParagraphProcessA(s, ctypes.byref(size), True)
        result_t_vector = ctypes.cast(result, ctypes.POINTER(nlpir.ResultT))
        words = []

        for i in range(0, size.value):
            r = result_t_vector[i]
            word = s[r.start:r.start + r.length]
            words.append((word, r.sPOS))

        f2 = open(output_path + item, 'w', encoding='utf-8')
        for word, pos in words:
            # try:
            if word.decode('utf-8') not in stop_set:
                if pos.decode('utf-8') > b'z'.decode('utf-8') or pos.decode('utf-8').upper() == pos.decode(
                        'utf-8') and pos.decode('utf-8') != '':
                    ans_lst.append((pos.decode('utf-8'), word.decode('utf-8')))
                f2.write((word.decode('utf-8') + '  ' + pos.decode('utf-8') + '\n'))
                f3.write((word.decode('utf-8') + '  ' + pos.decode('utf-8') + '\n'))
                # except:
                #     cnt1+=1
                # else:
                #     f2.write(word.decode('utf-8') + '\n')

        keys = pynlpir.get_key_words(s, max_words=10, weighted=False)
        ans_set = list(set(ans_lst))
        feqrence = [0 for k in range(len(ans_set))]
        for k in range(len(ans_set)):
            for item in ans_lst:
                if item == ans_set[k]:
                    feqrence[k] += 1
        f2.write('\n\nMy tags: ')
        type_lst = []
        for item in ans_set:  # ans_set:  ('COMPANY_OF_INDUSTRY_56', '兴业银行')
            if item[0] not in type_lst:
                type_lst.append(item[0])
        type_lst.sort()

        ans_s = ''
        for k in range(len(type_lst)):
            ans_s += str(type_lst[k]) + ': '
            for l in range(len(ans_set)):
                if ans_set[l][0] == type_lst[k]:
                    # 这里插入一个函数，来表示股票与基金间的关系
                    ans_s += stock2fund(ans_set, feqrence, l)
                    # ans_s+=' ('+str(ans_set[l][1])+': '+str(feqrence[l])+')'
            ans_s += '\n'
        f2.write(ans_s)
        f2.write('\n\nkeyword: ')

        # 这里是在数分词器给出的关键词词频
        keys_f = [0 for l in range(len(keys))]

        commen_last_name = ['王', '李', '张', '刘', '陈', '杨', '黄', '赵', '吴', '周', '徐', '孙', '马', '朱', '胡', '郭',
                            '何', '高', '林', '郑', '谢', '罗', '梁', '宋', '唐', '许', '韩', '冯', '邓', '曹', '彭', '曾',
                            '蕭', '田', '董', '袁', '潘', '于', '蒋', '蔡', '余', '杜', '叶', '程', '苏', '魏', '吕', '丁',
                            '任', '沈', '姚', '卢', '姜', '崔', '钟', '谭', '陆', '汪', '范', '金', '石', '廖', '贾', '夏',
                            '韦', '付', '方', '白', '邹', '孟', '熊', '秦', '邱', '江', '尹', '薛', '闫', '段', '雷', '侯',
                            '龙', '史', '陶', '黎', '贺', '顾', '毛', '郝', '龚', '邵', '万', '钱', '严', '覃', '武', '戴',
                            '莫', '孔', '向', '汤']
        ans3 = ''

        f3.seek(0)
        for line in f3:
            if len(line.split()) == 2:
                name = line.split()[0]
                pos = line.split()[1]
                for l in range(len(keys)):
                    if name == keys[l]:
                        keys_f[l] += 1
                if name[0] in commen_last_name and name not in ['万元', '周一', '周二', '周三', '周四', '周五', '周六', '周日',
                                                                '周天'] and len(name) in [2, 3] and pos == 'nr':
                    ans3 += '  ' + name

        ans2 = ''
        for l in range(len(keys)):
            ans2 += str(keys[l]) + ': ' + str(keys_f[l]) + '  '

        f2.write(ans2)
        f2.write('\n\nRelated person: ' + ans3)
        f2.close()

    pynlpir.close()
    return cnt1


input_path = 'C:/Users/i-zhanghaoran/Desktop/xml_pages2/'
output_path = 'C:/Users/i-zhanghaoran/Desktop/xml_pages3/'

stock_fund = load_fund_table('C:/Users/i-zhanghaoran/Desktop/content/')

print(partition(input_path, output_path))
