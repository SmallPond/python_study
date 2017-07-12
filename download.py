# !/usr/bin/env python
# _*_coding:utf-8 _*_


import urllib.request
# 正则表达式
import re


url = "https://tieba.baidu.com/p/5211831745"

# 获取HTML页面
def GetHtml(url):
    page = urllib.request.urlopen(url).read()
    page = page.decode('utf-8')
    return page

# 获取图片
def GetImg(html, page):
    reg = 'src="(.*\.jpg)" size'
    imgre = re.compile(reg)
    imglist = re.findall(imgre, html)
    print("正在下载第{0}页，此页面共有{1}张图片".format(page, len(imglist)))
    i = 1
    for imgurl in imglist:
       print("## 正在下载第{0}张图片".format(i))
       urllib.request.urlretrieve(imgurl, '{0}-{1}.jpg'.format(page, i))
       i += 1
    return imglist
'''
def GetNextUrl(html):
    # 匹配下一页
    reg = 'href="(.*pn=.)">下一页'
    nextUrlReg = re.compile(reg)
    nextUrl = re.findall(nextUrlReg, html)
    return nextUrl
'''
def GetNextUrl(html):
    reg = 'href=".*pn=(.)">下一页'
    nextUrlReg = re.compile(reg)
    nextPage = re.findall(nextUrlReg, html)
    nextUrl = url + "?pn={0}".format(nextPage[0])
    return nextUrl

def GetAllImg(url):
    page = 1
    html = GetHtml(url)
    while True:
        GetImg(html, page)
        page += 1
        nextUrl = GetNextUrl(html)
        if len(nextUrl) == 0:
            break
        html = GetHtml(nextUrl)


GetAllImg(url)
#html = GetHtml(url)
#print(GetNextUrl(html))
# print(GetNextUrl(html))


