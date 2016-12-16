#website使用说明



###简介：此项目是一个django网站，功能是一个文章的搜索，从本地的elasticsearch服务中获取与qurey最相关的结果并返回.网站只有主页和搜索结果页，挂在于django自带的server上，网站本身也不存储数据，每次查询都是从Mysql和elasticsearch上查询得到.

###文件与功能：因为只有两个页面所以很简单，一个mysql_con.py用restful连接es; 剩下的代码在views里，功能之一是可以直接搜索代码，此时就会用精确匹配，如果查询的代码是股票代码还是基金代码有歧义，就能返回超链接让用户再选一次;另一个功能是加入了时效性，使得更新的文章更容易出现.

###使用方法：本项目挂在/var/www/ 下. 实际上，我在/etc/init.d/路径下写了一个脚本website-run. 运行脚本，可以为root用户导入anaconda的运行环境、用--insecure参数运行django的生产模式、再用nohup守护进程. 当杀死进程的时候目前只能top -c查询，找一个带有anaconda路径的进程杀死.

###另：因为172.16.3.29只有8080一个向外的出口，如果要查看mysql数据库的时候可以关掉网站，然后把/etc/my.cnf 的ip改为0.0.0.0,端口改为8080即可.

###输出结果在/etc/rc.d/init.d/nohup.out，可以debug用

###另：git上的代码是DEBUG=True的（在setting.py中可以改成DEBUG=False，ALLOWED_HOSTS = ['*'],就成了生产模式，还要加上--insecure参数：$python manage.py runserver 0.0.0.0:8080 --insecure ，否则不会加载.css）
