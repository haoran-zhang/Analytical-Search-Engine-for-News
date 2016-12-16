# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urllib import request
from multiprocessing import Pool
import mysql.connector
import os

'''爬文章用的spider，初始化的时候输入时间，会爬前5页的目录，然后把符合时间的文章爬下来
用了5个进程并行，一页一个'''


class Spider:
    def __init__(self, path, date):  # path是项目目录，date是指定的哪一天的新闻
        self.root_dir = path
        self.SAVING_FOLDER = path + '/temp/xml_pages/'
        self.date = date

    def crawl_webpage(self, url):
        """
        根据具体文章的url来爬一篇文章
        """
        url2 = url.split('/')[-1]
        with request.urlopen(url) as f:
            data = f.read()
        try:
            soup = BeautifulSoup(data.decode('gb2312'), 'lxml')
        except:
            soup = BeautifulSoup(data, 'lxml')
        f2 = open(self.SAVING_FOLDER + url2[:-5], 'wb')
        f2.write((str(soup.head.title).split('_')[0] + '</title>\n').encode('utf-8'))

        for i in range(len(soup.find_all('meta')) - 1):
            item = soup.head.find_all('meta')[i]
            # print(item.attrs)
            if 'name' in item.attrs and item["name"] == "keywords":
                # print(('<keywords>'+str(item['content'])+'</keyword>'))

                f2.write(('<keyword>' + str(item['content']) + '</keyword>').encode('utf-8'))
            elif 'name' in item.attrs and item['name'] == 'description':
                f2.write(('<description>' + str(item['content']) + '</description>').encode('utf-8'))

        f2.write('<desc>'.encode('utf-8'))
        for i in range(len(soup.find_all('p')) - 1):
            item = soup.find_all('p')[i]
            if item.parent['class'] == ['Body']:
                s = str(item) + '\n'
                f2.write(s.encode('utf-8'))
        f2.write('</desc>'.encode('utf-8'))

        f2.close()

    def open_content(self, content_url, date):
        """
        输入目录页的url，传递到crawl——webpage中爬每一个具体文章
        """
        sub_url = []
        with request.urlopen(content_url)as f:
            data = f.read()
        soup = BeautifulSoup(data.decode('gb2312'), 'lxml')
        for link in soup.body.find_all('li'):
            if str(link.span).split()[0][:10] == '<span>2016':
                sub_url.append(link.a.get('href'))

        for item in sub_url:
            if date in item:  # 只爬有这个日期的文章
                try:
                    self.crawl_webpage('http://fund.eastmoney.com' + str(item))
                except Exception as e:
                    print('Exception is ', e)

    # open_content('http://fund.eastmoney.com/news/cjjyw.html')

    def run_spider(self):
        p = Pool(5)
        for i in range(1, 5):
            p.apply_async(self.open_content,
                          args=('http://fund.eastmoney.com/news/cjjyw_' + str(i) + '.html', self.date))  # 爬了前5页目录页
        p.close()
        p.join()
        print('CRAWL ALL DONE')

    def delete_duplicate(self):
        """
        这个函数用来查数据库中都爬过哪些文章了，然后把重复的从xml_pages中删掉
        """
        conn = mysql.connector.connect(user='chengxu', password='chengxu.gbh', database='nlp', host='127.0.0.1',
                                       port='3306')
        cursor = conn.cursor(buffered=True)

        cursor.execute("select url from news")
        values = cursor.fetchall()

        existed_lst = []
        for item in values:
            existed_lst.append(item[0].split('/')[-1][:-5])

        os.chdir(self.root_dir + '/temp/xml_pages')
        f_lst = os.listdir(os.getcwd())

        for item in f_lst:
            if item in existed_lst:
                os.remove(self.root_dir + '/temp/xml_pages/' + item)
