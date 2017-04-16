#!/usr/bin/python
# -*- coding: utf-8 -*-

import calendar
import datetime
import gc
import json
import re

import requests


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


def getJson(year=1995, month=1, day=1, newsType=0):
    if year == datetime.datetime.now().year and \
                    month == datetime.datetime.now().month and \
                    day == datetime.datetime.now().day:
        r = requests.get(getSiteURL(newsType)[1])
    else:
        r = requests.get(
            getSiteURL(newsType)[2] + dateFormat(
                year, month, day) + '/0.js')
    return r.text


def dateFormat(year=1995, month=1, day=1):
    dateString = datetime.date(year, month, day).isoformat().split('-')
    return dateString[0] + '-' + dateString[1] + '/' + dateString[2]


def jsonFormat(year=1995, month=1, day=1, newsType=0):
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
                    returnValue = list().append(
                        (list1[u'p'].split()[0], list1[u'p'].split()[1], getSiteURL(newsType)[0],
                         childClassification[list1[u'c']], list1[u'l'],
                         list1[u't']))
    return returnValue


def main():
    itemlist = list()
    for year in range(1995, datetime.datetime.now().year):
        for month in range(1, 12):
            for day in range(1, calendar.monthrange(year, month)[1]):
                for newsType in range(0, 6):
                    jsonlist = jsonFormat(year, month, day, newsType)
                    if jsonlist is None:
                        del jsonlist
                    else:
                        for items in jsonlist:
                            itemlist.append(items)
                        del jsonlist
                    gc.collect()


if __name__ == '__main__':
    main()
