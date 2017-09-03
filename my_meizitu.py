# _*_ coding:utf-8 _*_

# 2017.7.13 22：12
# 考虑加入多线程加快下载速度，待实现
# 使用多线程发现了问题： 关于文件操作，因我之前是顺序执行，导致文件不断嵌套创建
# 已利用OS模块获取当前路径而改进
# 不停的在不同文件夹下切换，是否会使速度减慢？
# 下一版本将加入 ， 可通过传入页面参数选择需要下载的页面
# python my_meizitu.py meizitu                # 创建的文件名


import sys
import os
import urllib.request
import re
import socket
import threading
import time
import urllib3

TIME = 10
socket.setdefaulttimeout(TIME)

NOW_PATH = ""

# 主页
url = "http://www.mzitu.com/mm/page/1"

class MyThread(threading.Thread):
    def __init__(self, target, url, name):
        print("## A New Thread")
        super(MyThread, self).__init__()       # 调用父类的构造函数
        self.target = target
        self.url = url
        self.name = name

    def run(self):
        self.target(self.url, self.name)


# 获取HTML页面
def get_html(url):
    '''
    :param url: 网站地址
    :return:    html页面
    '''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) Chrome/60.0.3112.90 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8',

    }
    time_count = 0
    req = urllib.request.Request(url=url, headers=headers)
    req.add_header('Referer', url)
    while True:
        try:
            page = urllib.request.urlopen(req).read()
            break
        except Exception as e:
            print("获取网页超时...")
            time_count += 1
            if time_count > 20:
                page = None
                print("获取网页失败")
                break
            time.sleep(1)                               # 等待20s
    page = page.decode('utf-8')
    return page

def get_album_url(html):
    '''
    获取各相册的URL
    :param html: 妹子图主页Html
    :return: 相册名List  相册URL_List
    '''
    # name已经测试成功
    album_name_reg = 'alt=\'(.+)\' src'
    album_name_re = re.compile(album_name_reg)
    album_name_list = re.findall(album_name_re, html)

    # url已经测试成功
    album_url_reg = r'href="(http://.+)" target.+alt'
    album_url_re = re.compile(album_url_reg)
    album_url_list = re.findall(album_url_re, html)
    return album_name_list, album_url_list


# 此正则表达式匹配可能有BUG， 若最大page数小于10，可能无法正确匹配
def get_album_max_page(album_url, album_html):
    '''
    :param album_url: 相册Url
    :param album_html: 相册的HTML
    :return: 相册的最大页数
    '''
    max_page_reg = r"href='{0}/(\d\d)'><span>".format(album_url)
    max_page_re = re.compile(max_page_reg)
    page_list = re.findall(max_page_re, album_html)
    max_page = max(page_list)
    return max_page

def get_img_url(html):
    reg = 'src="(.*\.jpg)" alt'
    imgre = re.compile(reg)
    imglist = re.findall(imgre, html)
    return imglist


def get_img(album_url, file_name):

    '''
    :param html: 相册第一页页面
    :param file_name: 创建的文件名
    :return: 无返回值
    '''

    PATH = NOW_PATH + "\\" + file_name
    album_html = get_html(album_url)        # 获取HTML页面
    try:
        os.mkdir(PATH)
    except Exception as e:
        print("{0}文件存在".format(file_name))
        return
    os.chdir(PATH)


    # 获取最大页数
    max_page = int(get_album_max_page(album_url, album_html))
    i = 1
    while(i <= max_page):
        # 此处重复解析了第一页，可以待改进
        album_url_temp = album_url + "/{0}".format(i)
        album_html = get_html(album_url_temp)

        # 网站可能会变化格式，此处用来调试
        # print(album_url)
        imglist = get_img_url(album_html)
        for img in imglist:
             print("正在下载第{0}张图片 -> {1}".format(i, file_name))
             # 解决盗链问题
             opener = urllib.request.build_opener()
             opener.addheaders = [('Referer',album_url_temp)]
             urllib.request.install_opener(opener)
             # 解决盗链问题
             urllib.request.urlretrieve(img, '{0}\{1}.jpg'.format(PATH, i))
        i += 1


# 获取整个相册的照片
def get_all_img(album_name_list, album_url_list):
    for album_name in album_name_list:
        for album_url in album_url_list:
            get_img(album_url, album_name)
            break


if __name__ == "__main__":
    '''
    主函数
    '''
    #file_name = str(sys.argv[1])
    file_name = "im_here"                 # 生成 exe格式不能传递参数
    try:
        os.mkdir(file_name)
    except Exception as e:
        print("文件夹 {0} 已经存在".format(file_name))
        #os.remove(file_name)
    os.chdir(file_name)

    NOW_PATH = os.path.abspath('.')              #获取当前工作目录
    home_html = get_html(url)
    album_name, album_url = get_album_url(home_html)

    ###########调试用###############
    # print(album_name[0])
    # print(album_url[0])
    # get_img(album_url[0], album_name[0])
    ###########调试用###############
    # 开启线程下载
    for (album_url_index, album_name_index) in zip(album_url, album_name):
        #get_img(album_url_index, album_name_index)
        my_thread = MyThread(get_img, album_url_index, album_name_index)
        my_thread.start()

