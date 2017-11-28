#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import urllib.request
import random
from bs4 import BeautifulSoup
import requests
import shutil
import os
from pron91pkg.disk import isDiskHasSpace
from pron91pkg.disk import convertToMB



"""
http 的基本功能
"""

BaseDownloadPath = "video/"

def prepareip():

    """
    生成一个随机的IP
    :return:
    """
    randIP = str(random.randint(0, 255)) + "." + str(random.randint(0,255)) + "." + str(random.randint(0,255)) + "." + str(random.randint(0,255))

    return randIP


def convertURL(url):

    """


    http://www.91porn.com/view_video.php?viewkey=35a6015bb91043b7ec91&page=&viewtype=&category=&action=comment

    格式化URL
    :param url: 视频详情的url
    :return:
    """
    words = url.split('&')

    url = words[0]

    url = url + "&action=comment"

    return url;


def fetchContent(url):


    """
    获取详情的页面内容
    :param url:
    :return:
    """
    randIP = prepareip()

    print(randIP)

    request_headers = {
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "X-Forwarded-For": randIP}

    # request_headers = {
    #     "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
    #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13",
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}




    print(url)
    request = urllib.request.Request(url,data=None,headers=request_headers)
    response = urllib.request.urlopen(request)

    rawHtml = response.read()

    return rawHtml


def fetchActualMessage(rawHtml):

    """
    获取片的信息
    :param rawHtml:
    :return:
    """


    soup = BeautifulSoup(rawHtml , "html.parser")


    titles = soup.find_all("div",id="viewvideo-title")

    dates = soup.find_all("option" , value = "date")


    title = titles[0].text.strip('\n')

    title=__escape_file_name_str(title)


    downloadURLs = soup.find_all("source")

    size = len(downloadURLs)

    result = None
    if size > 0 :
        print(title)

        url = downloadURLs[0]['src']
        print(url)

        types = downloadURLs[0]['type']

        type = types.split("/")[1]

        print(type)

        date = dates[0].text

        print(date)


        result = {
            "title":title,
            "date":date,
            "type":type,
            "downloadURL":url
        }
    else:
        print("超过限制")


    return result



def fecthActualPageMessage(rawHtml):


    """
    获取页面的信息
    """

    soup = BeautifulSoup(rawHtml , "html.parser")

    datas = soup.find_all("a" , target = "blank")

    # print(datas)

    list = []

    for one in datas :
        value = one['href']

        # print(one['title'])


        if"viewkey" in value:

            children = one.findChildren()
            # print(children)
            if children[0].has_attr('class'):

                list.append(one)

        # if"viewkey" in value and one.has_attr('title'):
        #     list.append(one)

    # print(list)

    urlList = []



    for one in  list:
        url = one['href']

        url = convertURL(url)

        urlList.append(url)

    currentPage = 0
    if len(urlList) > 0 :
        ss = urlList[0].split("&")
        for one in ss:
            if "page" in one:
                value = one
                value = value.split("=")[1]
                currentPage = value


    result = {

        "currentPage":currentPage,
        "size": len(list),
        "urls":urlList
    }


    print(result)
    return result

def downloadVideo(url, file_name):
    """
    下载文件夹
    """

    targetPath = BaseDownloadPath

    try:
        os.makedirs(targetPath,0o0755);
    except FileExistsError:
        print("下载目录存在")

    targetPath = targetPath + file_name

    try:
        file = open(targetPath, 'r')
        file.close()
        os.remove(targetPath)
    except FileNotFoundError:
        print("")


    response = requests.get(url, stream=True)



    fileSize = int(response.headers['content-length'])
    isHaveSpace = isDiskHasSpace(byteValue=fileSize)

    print(str(convertToMB(value=fileSize)) + "MB")
    print("-------------")

    if isHaveSpace:
        with open(targetPath, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
            del response
    else:

        del response
    return isHaveSpace

def __escape_file_name_str(file_name):
    """
    去除文件名中的特殊字符
        Args:
            file_name (str): 文件名
    """

    while file_name.find('/') >= 0:
        file_name = file_name.replace('/', '')

    while file_name.find('\\') >= 0:
        file_name = file_name.replace('\\', '')

    return file_name



def fetchMaxPageNumber(rawHtml):


    """
    获取最大页码
    """
    soup = BeautifulSoup(rawHtml , "html.parser")
    target = soup.find_all("div",class_="pagingnav")

    pages = target[0].find_all("a")


    number = 0
    for one in pages :
        value = one.text
        if value.isnumeric():
            valueInt = int(value)
            if valueInt > number :
                number = valueInt


    return number

def isPageNaviHasNext(rawHtml):
    soup = BeautifulSoup(rawHtml , "html.parser")
    target = soup.find_all("div",class_="pagingnav")

    pages = target[0].find_all("a")


    pageContent = str(pages)
    # print(pageContent)


    if "»" in pageContent:
        hasNext = True


    else:
        hasNext = False

    return hasNext


