# Auto_update 使用文档



###简述：此项目抽取了之前的Emotional_Analysis和Spider项目的文件组成，目的是自动从东方财富网爬取新闻、做情感分析并抽取关键词、最后导入Mysql和Elasticsearch中.


####项目保存在/var/www路径下.项目加入了root用户的crontab，输出结果在/root/auto_run_data.log.(运行crond  #/sbin/service crond reload)


###常见问题：
####1,pynlpir出现init错误：
####这是因为NLPIR的证书只有一个月有效期，去他们的github页面https://github.com/NLPIR-team/NLPIR/tree/master/License 下载证书，替换掉/home/dev/anaconda3/lib/python3.5/site-packages/pynlpir/Data的文件即可
####2,如果需要新建一个es的index（类比mysql的一张表）：
####需要用到mysql_es.py中的create_index方法。另外，我用了ik这个分词器，所以之前还需要配置一下，具体可见https://github.com/medcl/elasticsearch-analysis-ik 的常见问题“如何手动安装”（服务器里有编译好的.jar,直接拷贝用也行）另，如果报错，可能还需要安装新版本的java



###Pipeline分为6步：
####1.爬下网页：这个调用了spider.py文件：输入一个日期，爬下东方财富网的前5页目录页的文章，留下在这个日期爬下的而且没有之前被爬过的文章，放入/temp/xml_pages文件夹
####2&3,分词、情感分析：简单的清洗之后，数据放入xml_pages2.之后通过partition_main_character.py 和emotional_analysis.py来分析. 
####分析文章的主元素，即一篇文章只有主要与一家公司或者一个行业相关，才会被选入。这样很大程度的避免了那种“最近涨势最好的10支股票”这样主题分散的文章。大概有一半的文章是仅有一个主题的。具体的算法
####分词和情感分析：分词用的是NLPIR这个库，加上自己的关键词效果还不错。情感分析的话，还是通过数正负极性词来判断（也用函数调整了一下情感值分布，然而原理上还只是数词频）。虽然用了很多词典，但是难点还在于词典不够。总之最后效果还行。
####用到的外部文件：fund_stock文件夹，用来保存每只基金都买了哪些股票的信息，在Mysql数据库中也有;new_bigdic.txt，用户字典，收录了公司名称和行业名称作为关键字，这样分词器可以识别并输出这些关键字;stop_list.txt，停止词，分词之后用;merge_pos,merge_neg,senti_dic，都是情感词典，用了知网的词典、台大的词典和学生褒贬词典，以及手工标注了一些高频的金融上用的词。

####4,导入mysql:把/temp中的几个文件夹导入mysql中，这样mysql中就全部是结构化的而且分析好的数据
####5,导入elasticsearch:从Mysql下载数据并一条条插入本机的es中.Es类中保留了create_mapping的方法，如果要重新建立本机的es就可以重建mapping，平时自动更新的时候不需要.
####6,清理临时文件：清理/temp下的几个文件夹，因为涉及了文件操作，所以运行的时候需要root权限.不过用文件夹的好处是每一个文件是独立的，如果文件处理出错直接跳过这个文件就行，容错很好(错误经过这么久调试并不多了)










Some day I will translate it ......