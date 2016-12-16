# -*- coding: utf-8 -*-
import time
import os
import pytz
from datetime import datetime

'''
这个脚本用来串起几个程序成一个pipeline，来自动更新文章
'''

root_dir = '/var/www/auto_update'  # 项目存放的位置，硬编码

# 设置时区
tz = pytz.timezone('Asia/Shanghai')
now = datetime.now(tz)
current_time = now.strftime('20%y%m%d %H:%M')
date = now.strftime('20%y%m%d')

print('HERE IS pid %s' % os.getpid())  # 写入日志
print('Start at ', current_time)


def time_consume(func):  # 一个记录时间用的装饰器
    def wrapper(*args, **kw):
        start = time.time()
        func(*args, **kw)
        stop = time.time()
        print('Function %s(): done!' % func.__name__)
        print('Time consume: ', stop - start)
    return wrapper


def clean_temp(path):  # 用来清除一个文件夹下的所有文件
    os.chdir(root_dir + path)
    f_lst = os.listdir(os.getcwd())
    for item in f_lst:
        os.remove(item)


@time_consume
def auto_run(date):
    try:
        # first, crawl the web
        from spider import Spider
        s = Spider(root_dir, date)
        s.run_spider()
        s.delete_duplicate()

        # second, partition & main character
        from nlp.xml_to_pure_text import clean_data
        clean_data(root_dir)

        from nlp.partition_main_character import Partition
        p = Partition(root_dir)
        p.main()

        # third, emotional analysis
        from nlp.emotional_analysis_new import emotional_analysis
        emotional_analysis(root_dir)

        # forth, add anything to mysql
        from mysql_connector.fund2news_mysql import fund2news
        fund2news(root_dir)

        from mysql_connector.news_mysql import news
        news(root_dir)

        from mysql_connector.news_info_mysql import news_info
        news_info(root_dir)

        # fifth, insert into elastic search
        from mysql_es import Es
        e = Es(root_dir)
        e.main()
        print('All things done!!')

    except Exception  as e:
        print('Exceptions occur!!', e)

    finally:
        # sixth, clean temp file
        clean_temp('/temp/xml_pages')
        clean_temp('/temp/xml_pages2')
        clean_temp('/temp/xml_pages3')
        clean_temp('/temp/xml_pages4')


auto_run(date)
