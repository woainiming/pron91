#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pron91pkg.pron91 import Pron91
from pron91pkg.databasemanager import Databasemanager
import time
from datetime import datetime
import traceback
import sys, os
import subprocess
from time import gmtime, strftime

SLEEP_per_30_min = 10000 * 30
SLEEP_per_page = 10
initURL = "http://91porn.com/v.php?next=watch&page=4089"



# def AmIRunning():
#     out_bytes = subprocess.check_output('ps -ef | grep python3', shell=True)
#     text = out_bytes.decode('utf-8')
#     fileName = os.path.abspath(sys.argv[0])
#
#     if fileName in text:
#         return True
#     else:
#         return False

def main():



    pron = Pron91();

    # pron.fetch_home_page()
    #
    # pron.fetchTargetPage("http://www.91porn.com/v.php?&page=4058")
    #
    # pron.fetchPageNumber(4051)
    #
    # result = pron.fetch("http://91porn.com/view_video.php?viewkey=b5781e9ea815cdd633e5&page=4058&viewtype=basic&category=mr")
    #
    #
    # name = result["title"] + "."+result["type"]
    #
    # httputil.downloadVideo(result['downloadURL'],name)


# http://91.7h5.space/v.php?next=watch&page=4088
    db = Databasemanager()
    maxPageNumber = pron.fetchMaxPageNumber(initURL)

    db.updatePageSize(size=maxPageNumber)

    maxPageNumber = db.getDBPageSize()
    currentPageIndex = db.getDBPageIndex()

    print("PageSize:"+str(maxPageNumber))

    print("PageIndex:"+str(currentPageIndex))
    print("DB Path:"+db.getDBPath())

    readNum = maxPageNumber - currentPageIndex

    # datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    startTime = datetime.now()

    while(readNum > 0):

        result = pron.fetchPageNumber(readNum)
        urls = result['urls']

        for url in urls:
            viewkey = url.split('viewkey=')[1]
            viewkey = viewkey.split('&')[0]

            pronData = {
                "viewkey":viewkey,
                "originalURL":url,
                "title":"",
                "type":"",
                "actDownloadURL":"",
                "downloadStatus":"0"
            }

            db.insertOrUpdatePron(pronData)
        currentPageIndex = currentPageIndex + 1
        db.updatePageIndex(currentPageIndex)

        #check max page

        nowMaxPageNumber = pron.fetchMaxPageNumber(initURL)

        if (nowMaxPageNumber != maxPageNumber):
            pageDiff = nowMaxPageNumber - maxPageNumber
            currentPageIndex = currentPageIndex - pageDiff
            maxPageNumber = nowMaxPageNumber



        readNum = maxPageNumber - currentPageIndex

        print("Current get page:" + str(currentPageIndex))
        nowTimt = datetime.now()

        diff = nowTimt - startTime

        # if (diff > SLEEP_per_30_min):
        #     startTime = datetime.now()
        #     time.sleep(SLEEP_per_30_min)
        # else:
        #     time.sleep(SLEEP_per_page)
        time.sleep(SLEEP_per_page)


    #end while

    print("End")

def generateLogPath():

    pathName = os.path.dirname(sys.argv[0])

    strTime = strftime("%Y-%m-%d %H-%M-%S", gmtime())

    directory = pathName + "/crash/"
    logFilePath =  directory + strTime+"log.txt"

    if not os.path.exists(directory):
        os.makedirs(directory)
    return logFilePath


if __name__ == '__main__':

    logFilePath = generateLogPath()
    #This line opens a log file
    log = open(logFilePath, "w")
    try:

        main()
        # if AmIRunning():
        #     print("I am Running")
        # else:
        #     print("I am not Running")
        #     main()

    except Exception:
        traceback.print_exc(file=log)