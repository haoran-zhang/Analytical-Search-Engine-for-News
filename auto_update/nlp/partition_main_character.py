#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pynlpir
import ctypes
import os
import tempfile
import pickle
from bs4 import BeautifulSoup

'''
这个文件是调用nlpir和自己写的字典, bigdic.txt来做分词和关键词提取
'''


class Partition:
    def __init__(self, path):  # 用项目路径来初始化
        self.root_dir = path

    def load_fund_table(self, folder_path):
        """
        导入  基金--股票 的数据，存在fund——stock文件夹内
        """
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

    def stock2fund(self, ans_set, frequency, l):
        """
        这个是用来数每支股票属于几家基金
        """
        related_fund = []
        s = ''
        s += ' (' + str(ans_set[l][1]) + ': ' + str(frequency[l]) + ')'
        if ans_set[l][0][:7] == 'COMPANY':
            stock_name = ans_set[l][1]
            for i in range(len(stock_fund)):
                if stock_fund[i][1] and stock_name in stock_fund[i][1]:
                    related_fund.append(stock_fund[i][0])
            s += '\nRelated_fund: ' + ','.join(related_fund)
            s += '\n'
        return s

    def select_main_character(self, f_item, ans_set, frequency):
        """
        从文章中众多元素中抽出最主要相关的行业、个股， 如果主题特别分散，就丢弃这篇
        :param f_item: 这篇文章的id，用这个id打开原始爬下来的xml文件，去检查title，meta，keyword有没有关键词
        :param ans_set: 抽出来的关键词  例如：ans_set:  ('COMPANY_OF_INDUSTRY_56', '兴业银行')
        :param frequency: 关键词的词频
        :return:
        """
        main_company = []
        main_industry = []
        keyword = ''
        # step 1 检查是否在title,keyword,meta中出现
        with open(self.root_dir + '/temp/xml_pages/' + f_item, encoding='utf-8') as f:
            data = f.read()
        soup = BeautifulSoup(data, 'lxml')
        title = ','.join(soup.title.text.split())
        if soup.keyword:
            keyword = ','.join(soup.keyword.text.split())
        for _ in range(len(ans_set)):
            if ans_set[_][1] in title or keyword and ans_set[_][1] in keyword:
                if ans_set[_][0][:7] == 'COMPANY':
                    main_company.append((ans_set[_], frequency[_]))
                elif ans_set[_][0][:8] == 'INDUSTRY':
                    main_industry.append((ans_set[_], frequency[_]))

        if main_industry != [] or main_company != []:
            return (main_company, main_industry)

        i_ans_set = []  # 把ans_set中的种类挑出company和industry两种，并把这两种分开
        i_frequency = []

        try:
            length = len(ans_set)
            i = 0
            while i < length:
                if ans_set[i][0][:7] != 'COMPANY':
                    item = ans_set.pop(i)
                    fre = frequency.pop(i)
                    length -= 1
                    i -= 1
                    if item[0][:8] == 'INDUSTRY':
                        i_ans_set.append(item)
                        i_frequency.append(fre)
                i += 1

        except Exception as e:
            print(e, ans_set)

        # 这里的算法是，出现的频率超过50%的元素就是主要元素了
        if frequency:
            index = frequency.index(max(frequency))
            if 1.0 * frequency[index] / sum(frequency) >= 0.5:
                main_company.append((ans_set[index], frequency[index]))

        if i_frequency:
            index = i_frequency.index(max(i_frequency))
            if 1.0 * i_frequency[index] / sum(i_frequency) >= 0.5:
                main_industry.append((i_ans_set[index], i_frequency[index]))

        if main_company != [] or main_industry != []:
            return (main_company, main_industry)

    def partition(self, input_path, output_path):
        """
        分词，把input _path 里的文本文件分词，结果存在output_path
        :param input_path: 文本文件路径
        :param output_path: 分词结果的路径
        :return: 编码错误的词的错误
        """
        f3 = tempfile.NamedTemporaryFile(mode='w+t', encoding='utf-8')
        f3_name = f3.name

        stop_set = []
        f_stop_list = open(self.root_dir + '/nlp/stop_list.txt', 'r', encoding='utf-8')
        for line in f_stop_list:
            if line.split():
                stop_set.append(line.split()[0])
        stop_set = set(stop_set)

        os.chdir(input_path)
        f_lst = os.listdir(os.getcwd())
        cnt1 = 0
        nlpir = pynlpir.nlpir
        pynlpir.open()

        big_dic = self.root_dir + '/nlp/new_bigdic.txt'
        nlpir.ImportUserDict(big_dic.encode('utf-8'))

        for f_item in f_lst:
            try:
                ans_lst = []
                f = open(f_item, 'r', encoding='utf-8')
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

                for word, pos in words:
                    # try:
                    if word.decode('utf-8') not in stop_set:
                        if pos.decode('utf-8') > b'z'.decode('utf-8') or pos.decode('utf-8').upper() == pos.decode(
                                'utf-8') and pos.decode('utf-8') != '':
                            ans_lst.append((pos.decode('utf-8'), word.decode('utf-8')))

                        f3.write((word.decode('utf-8') + '  ' + pos.decode('utf-8') + '\n'))

                keys = pynlpir.get_key_words(s, max_words=10, weighted=False)
                ans_set = list(set(ans_lst))
                frequency = [0 for k in range(len(ans_set))]
                for k in range(len(ans_set)):
                    for item in ans_lst:
                        if item == ans_set[k]:
                            frequency[k] += 1

                type_lst = []
                for item in ans_set:  # ans_set:  ('COMPANY_OF_INDUSTRY_56', '兴业银行')
                    if item[0] not in type_lst:
                        type_lst.append(item[0])
                type_lst.sort()

                ans_s = ''
                main_character = self.select_main_character(f_item, ans_set, frequency)
                # print('return things',main_character)
                if main_character:
                    f2 = open(output_path + f_item, 'w', encoding='utf-8')
                    main_company = main_character[0]
                    main_industry = main_character[1]
                    if main_company:
                        ans_s += 'Main company:  '
                        for _ in range(len(main_company)):
                            ans_s += str(main_company[_][0][1]) + '\t' + str(main_company[_][0][0])
                        ans_s += '\n'

                    if main_industry:
                        ans_s += 'Main industry:  '
                        for _ in range(len(main_industry)):
                            ans_s += str(main_industry[_][0][1]) + '\t' + str(main_industry[_][0][0])
                        ans_s += '\n'

                    f2.write(ans_s)
                    # 如果这两个同时为空，那么就是无主题的了，抛弃之


                    # 这里是在数分词器给出的关键词词频
                    keys_f = [0 for l in range(len(keys))]

                    # 这里是找文中出现的人名，同时数了关键词的词频
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
                                    # if name[0] in commen_last_name and name not in ['万元','周一','周二','周三','周四','周五','周六','周日','周天'] and len(name) in [2,3] and pos=='nr':
                                    #     ans3+='  '+name

                    ans2 = 'Key words:  '
                    for l in range(len(keys)):
                        ans2 += str(keys[l]) + ': ' + str(keys_f[l]) + '  '

                    f2.write(ans2)
                    # f2.write('\n\nRelated person: '+ans3)
                    f2.close()
                else:
                    continue
            except Exception as e:
                print('Exception in partition_main_character', e)
        pynlpir.close()
        return cnt1

    def partition_original(self, input_path, output_path):
        """
        分词，把input _path 里的文本文件分词，结果存在output_path
        和上一个函数的输出路径不相同，这个会保存分词的结果
        """
        f3 = tempfile.NamedTemporaryFile(mode='w+t', encoding='utf-8')
        f3_name = f3.name

        stop_set = []
        f_stop_list = open(
            self.root_dir + '/nlp/stop_list.txt', 'r',
            encoding='utf-8')
        for line in f_stop_list:
            if line.split():
                stop_set.append(line.split()[0])
        stop_set = set(stop_set)

        os.chdir(input_path)
        f_lst = os.listdir(os.getcwd())
        cnt1 = 0
        nlpir = pynlpir.nlpir
        pynlpir.open()

        big_dic = self.root_dir + '/nlp/new_bigdic.txt'
        nlpir.ImportUserDict(big_dic.encode('utf-8'))  # 导入用户词典

        for item in f_lst:
            try:
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

                keys = pynlpir.get_key_words(s, max_words=10, weighted=False)
                ans_set = list(set(ans_lst))
                feqrence = [0 for k in range(len(ans_set))]
                for k in range(len(ans_set)):
                    for item in ans_lst:
                        if item == ans_set[k]:
                            feqrence[k] += 1
                f2.write('\n\nMy tags: ')
                type_lst = []
                for item in ans_set:  #输出结果举例： ans_set:  ('COMPANY_OF_INDUSTRY_56', '兴业银行')
                    if item[0] not in type_lst:
                        type_lst.append(item[0])
                type_lst.sort()

                ans_s = ''
                for k in range(len(type_lst)):
                    ans_s += str(type_lst[k]) + ': '
                    for l in range(len(ans_set)):
                        if ans_set[l][0] == type_lst[k]:
                            # 这里插入一个函数，来表示股票与基金间的关系
                            ans_s += self.stock2fund(ans_set, feqrence, l)
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
            except Exception as e:
                print('Exception in partition_main_character', e)

        pynlpir.close()
        return cnt1

    def main(self):
        global stock_fund
        input_path = self.root_dir + '/temp/xml_pages2/'
        output_path = self.root_dir + '/temp/xml_pages4/'
        output_path2 = self.root_dir + '/temp/xml_pages3/'

        stock_fund = self.load_fund_table(self.root_dir + '/nlp/fund_stock/')  # 这个文件夹里是股票与基金的对应关系

        print('Times of error during partition:')
        print(self.partition(input_path, output_path))
        print(self.partition_original(input_path, output_path2))
