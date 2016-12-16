# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import os
'''简单的洗数据'''


def clean_data(root_dir):
    os.chdir(root_dir + '/temp/xml_pages/')
    f_list = os.listdir(os.getcwd())

    for f_item in f_list:
        try:
            f2 = open(root_dir + '/temp/xml_pages2/' + f_item, 'w', encoding='utf-8')
            with open(f_item, encoding='utf-8') as f:
                data = f.read()
            soup = BeautifulSoup(data, 'lxml')
            title = ','.join(soup.title.text.split()) + '。'
            keyword = ''
            if soup.keyword:
                keyword = ','.join(soup.keyword.text.split()) + '。'
            meta = ','.join(soup.description.text.split()) + '。'
            text = ''
            p_list = soup.find_all('p')
            for item2 in p_list:
                if "点击" not in item2.text and "责任编辑" not in item2.text and ">>" not in item2.text:
                    text += item2.text
            # print(title,keyword,meta,text)
            text = text.replace(' ', '')
            text = text.replace('\n', '')
            text = text.replace('\t', '')

            f2.write(title)
            f2.write('\n\n')
            f2.write(keyword)
            f2.write('\n\n')
            f2.write(meta)
            f2.write('\n\n')
            f2.write(text)
            f2.close()
        except Exception as e:
            print('Error at xml 2 pure text', e)
