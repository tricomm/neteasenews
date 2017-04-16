#!/usr/bin/python
# -*- coding: utf-8 -*-

import calendar
import datetime
import gc
import json
import re

import requests
from pymongo import *

from basenews import getanews


def getSiteURL(sitename=0):
    siteList = [['新闻', 'http://news.163.com/special/0001220O/news_json.js',
                 'http://snapshot.news.163.com/wgethtml/http+!!news.163.com!special!0001220O!news_json.js/'],
                ['娱乐', 'http://ent.163.com/special/00032IAD/ent_json.js',
                 'http://snapshot.news.163.com/wgethtml/http+!!ent.163.com!special!00032IAD!ent_json.js/'],
                ['体育', 'http://sports.163.com/special/0005rt/news_json.js',
                 'http://snapshot.news.163.com/wgethtml/http+!!sports.163.com!special!0005rt!news_json.js/'],
                ['财经', 'http://money.163.com/special/00251G8F/news_json.js',
                 'http://snapshot.news.163.com/wgethtml/http+!!money.163.com!special!00251G8F!news_json.js/'],
                ['科技', 'http://tech.163.com/special/00094IHV/news_json.js',
                 'http://snapshot.news.163.com/wgethtml/http+!!tech.163.com!special!00094IHV!news_json.js/'],
                ['手机', 'http://mobile.163.com/special/00112GHS/phone_json.js',
                 'http://snapshot.news.163.com/wgethtml/http+!!tech.163.com!mobile!special!00112GHS!phone_json.js/'],
                ['女人', 'http://lady.163.com/special/00264IIC/lady_json.js',
                 'http://snapshot.news.163.com/wgethtml/http+!!lady.163.com!special!00264IIC!lady_json.js/']]
    return siteList[sitename]


def getChildClassification(category):
    returnValue = list()
    for elem in category:
        returnValue.append(elem[u'n'])
    return returnValue


def getJson(year=2014, month=1, day=1, newsType=0):
    if year == datetime.datetime.now().year and \
                    month == datetime.datetime.now().month and \
                    day == datetime.datetime.now().day:
        r = requests.get(getSiteURL(newsType)[1])
    else:
        r = requests.get(
            getSiteURL(newsType)[2] + dateFormat(
                year, month, day) + '/0.js')
    return r.text


def dateFormat(year=2014, month=1, day=1):
    dateString = datetime.date(year, month, day).isoformat().split('-')
    return dateString[0] + '-' + dateString[1] + '/' + dateString[2]


def jsonFormat(year=2014, month=1, day=1, newsType=0):
    text = getJson(year, month, day, newsType)
    returnValue = list()
    if text.startswith('var data=') is True:
        tmp = re.sub(',*,', ',', text.lstrip('var data=').rstrip(';').replace('\n', '').replace(',[]', ''))
        tmpValue = json.loads(tmp)
        childClassification = getChildClassification(tmpValue[u'category'])
        for list0 in tmpValue[u'news']:
            for list1 in list0:
                if list1[u'l'].find('photoview'):
                    continue
                else:
                    # 插入的格式是 日期,时间,分类,子分类,URL,标题
                    returnValue = list().append(
                        [list1[u'p'].split()[0], list1[u'p'].split()[1], getSiteURL(newsType)[0],
                         childClassification[list1[u'c']], list1[u'l'],
                         list1[u't']])
    return returnValue


def sendToMongodb(insertData):
    db = MongoClient().client['neteasenews']
    collection = db['news']
    collection.insert_one(insertData)


# 网易的接口最多只能获取到2014年3月22日的新闻。再往前也有对应的接口，不过已经无法工作
# 如果改用腾讯的接口，虽然能获取到2009年1月1日的新闻，但网页处理方面比较麻烦（主要是腾讯的网页改过版），放弃
def main():
    for year in range(2014, datetime.datetime.now().year):
        for month in range(1, 12):
            for day in range(1, calendar.monthrange(year, month)[1]):
                for newsType in range(0, 6):
                    jsonlist = jsonFormat(year, month, day, newsType)
                    if jsonlist is not None:
                        for items in jsonlist:
                            if items[4].find('photoview') is -1 or items[4].find('blog') is -1:
                                sendToMongodb(
                                    {'date': items[0], 'time': items[1], 'class': items[2], 'childclass': items[3],
                                     'url': items[4], 'title': items[5], 'content': getanews(items[4])})
                    del jsonlist
                    gc.collect()


if __name__ == '__main__':
    main()
