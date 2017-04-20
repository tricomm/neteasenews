#!/usr/bin/python
# -*- coding: utf-8 -*-

import calendar
import datetime
import gc
import json
import re

import requests
from bs4 import BeautifulSoup
from pymongo import *


def getSiteURL(sitename=0):
    siteList = [[u'新闻', 'http://news.163.com/special/0001220O/news_json.js',
                 'http://snapshot.news.163.com/wgethtml/http+!!news.163.com!special!0001220O!news_json.js/'],
                [u'娱乐', 'http://ent.163.com/special/00032IAD/ent_json.js',
                 'http://snapshot.news.163.com/wgethtml/http+!!ent.163.com!special!00032IAD!ent_json.js/'],
                [u'体育', 'http://sports.163.com/special/0005rt/news_json.js',
                 'http://snapshot.news.163.com/wgethtml/http+!!sports.163.com!special!0005rt!news_json.js/'],
                [u'财经', 'http://money.163.com/special/00251G8F/news_json.js',
                 'http://snapshot.news.163.com/wgethtml/http+!!money.163.com!special!00251G8F!news_json.js/'],
                [u'科技', 'http://tech.163.com/special/00094IHV/news_json.js',
                 'http://snapshot.news.163.com/wgethtml/http+!!tech.163.com!special!00094IHV!news_json.js/'],
                [u'手机', 'http://mobile.163.com/special/00112GHS/phone_json.js',
                 'http://snapshot.news.163.com/wgethtml/http+!!tech.163.com!mobile!special!00112GHS!phone_json.js/'],
                [u'女人', 'http://lady.163.com/special/00264IIC/lady_json.js',
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
        if newsType is not 0:
            tmp = re.sub(r'(,|\{)([a-z]*?)(:)', r'\1"\2"\3', tmp)
            tmp = re.sub(r'(\[),(\{)', r'\1\2', tmp.replace('\\', '/'))
        try:
            tmpValue = json.loads(tmp, strict=False)
        except:
            return list()
        childClassification = getChildClassification(tmpValue[u'category'])
        if newsType is 1:
            valuelist = tmpValue[u'ent']
        else:
            valuelist = tmpValue[u'news']
        for list0 in valuelist:
            for list1 in list0:
                if list1 is not None:
                    if list1[u'l'].find('photoview') is -1 and list1[u'l'].find('blog') is -1:
                        returnValue.append(
                            [list1[u'p'].split()[0], list1[u'p'].split()[1], getSiteURL(newsType)[0],
                             childClassification[list1[u'c']], list1[u'l'],
                             list1[u't']])
    return returnValue


def sendToMongodb(insertData):
    db = MongoClient()
    collection = db.client['neteasenews']['news']
    collection.insert_one(insertData)
    db.close()


def getnews(URL):
    date = str()
    html = requests.get(URL)
    soup = BeautifulSoup(html.text, 'html.parser')
    alls = soup.find_all('div', id="endText")
    for div in alls:         #re.compile("p")
        for p_tag in div.find_all('p'):
            if not p_tag.has_attr('class'):
                if not p_tag.string is None:
                    #print ('\n'+p_tag.text)
                    date += p_tag.text + u'\n'
    return date

# 网易的接口最多只能获取到2014年3月22日的新闻。再往前也有对应的接口，不过已经无法工作
# 如果改用腾讯的接口，虽然能获取到2009年1月1日的新闻，但网页处理方面比较麻烦（主要是腾讯的网页改过版），放弃
def main():
    for year in range(2014, datetime.datetime.now().year + 1):
        for month in range(1, 13):
            for day in range(1, calendar.monthrange(year, month)[1] + 1):
                for newsType in range(0, 7):
                    jsonlist = jsonFormat(year=year, month=month, day=day, newsType=newsType)
                    if len(jsonlist) is not 0:
                        for items in jsonlist:
                            sendToMongodb(
                                {'date': items[0], 'time': items[1], 'class': items[2], 'childclass': items[3],
                                 'url': items[4], 'title': items[5], 'content': getnews(str(items[4]))})
                        del jsonlist
                        gc.collect()


if __name__ == '__main__':
    main()
