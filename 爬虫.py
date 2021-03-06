
from bs4 import BeautifulSoup  # 网页解析，获取数据
import re  # 正则表达式，进行文字匹配
import urllib.request, urllib.error  # 指定URL，获取网页数据
import sqlite3  # 进行SQLite数据库操作


def main():
    baseurl = "https://movie.douban.com/top250?start="
    datalist = getData(baseurl)
    dbpath = "movie.db"
    saveData2DB(datalist, dbpath)

    # 1.爬取网页


# 影片链接
Link = re.compile(r'<a href="(.*)">')  # 创建正则表达式对象，表示规则（字符串的模式）
# 影片图片
ImgSrc = re.compile(r'<img.*src="(.*?)"', re.S)  # re.S 让换行符包含在字符中
# 影片片名
Title = re.compile(r'<span class="title">(.*)</span>')
# 影片评分
Rating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
# 评价人数
Judge = re.compile(r'<span>(\d*)人评价</span>')
# 概况
Inq = re.compile(r'<span class="inq">(.*)</span>')
# 影片的相关内容
Bd = re.compile(r'<p class="">(.*?)</p>', re.S)


def getData(baseurl):
    datalist = []
    for i in range(0, 10):  # 获取页面信息10次
        url = baseurl + str(i * 25)
        html = askURl(url)  # 保存获取到的网页源码

        # 逐一解析
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all('div', class_="item"):
            data = []  # 保存一部电影的所有信息
            item = str(item)

            # 影片的链接
            link = re.findall(Link, item)[0]  # 括号中的第一项是正则表达式，第二项是字符串
            data.append(link)  # 添加链接

            imgSrc = re.findall(ImgSrc, item)[0]
            data.append(imgSrc)  # 添加照片

            titles = re.findall(Title, item)  # 片名可能只有中文名，没有外国名
            if (len(titles) == 2):
                ctitle = titles[0]
                data.append(ctitle)
                otitle = titles[1].replace("/", "")
                data.append(otitle)
            else:
                data.append(titles[0])
                data.append('')  # 外国名字留空

            rating = re.findall(Rating, item)[0]
            data.append(rating)  # 添加评分

            judgeNum = re.findall(Judge, item)[0]
            data.append(rating)  # 评分人数

            inq = re.findall(Inq, item)
            if len(inq) != 0:
                inq = inq[0].replace("。", "")
                data.append(inq)  # 添加概述
            else:
                data.append("")

            bd = re.findall(Bd, item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?', " ", bd)  # 去掉<br/>
            bd = re.sub('/', " ", bd)  # 替换/
            data.append(bd.strip())  # 去掉前后的空格

            datalist.append(data)  # 把处理好的一部电影信息放入datalist

    return datalist


# 得到指定的一个URL的网页内容
def askURl(url):
    head = {
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 80.0.3987.122  Safari / 537.36"
    }

    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html


# 创建数据库
def init_db(dbpath):
    sql = '''
         create table movie250 
        (
        id integer primary key autoincrement ,
        info_link text ,
        pic_link text ,
        cname varchar ,
        ename varchar ,
        score numeric ,
        rated numeric ,
        instroduction text ,
        info text
        )


        '''  # 创建数据表

    conn = sqlite3.connect(dbpath)  # 去链接这个数据库文件
    cursor = conn.cursor()  # 游标操作
    cursor.execute(sql)
    conn.commit()
    conn.close()

# 保存数据

def saveData2DB(datalist, dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    for data in datalist:
        for index in range(len(data)):
            if index == 4 or index == 5:
                continue
            data[index] = '"' + data[index] + '"'
        sql = '''
                insert into movie250 (
                info_link,pic_link,cname,ename,score,rated,instroduction,info) 
                values(%s)''' % ",".join(data)
        print(sql)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    # 调用
    main()
```
