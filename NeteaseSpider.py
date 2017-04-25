#!/usr/bin/python
# -*- coding: utf-8 -*-

import calendar
import datetime
import gc
import json
import random

import multiprocessing
import regex as re

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


## 由于程序经常因为网络原因崩溃，所以把所有网络处理的部分集中到一个函数。
## 如果这个方法依旧不行就考虑按照TODO列表里的Save&Load大法
def networkExceptionCatch(url):
    while True:
        try:
            ## 地址后加一个看起来没卵用的随机数是为了防止运营商的缓存命中。
            ## 一旦命中，返回的东西鬼知道是什么
            r = requests.get(url + '?' + str(random.random()))
        except:
            continue
        break
    return r.text


def getChildClassification(category):
    returnValue = list()
    for elem in category:
        returnValue.append(elem[u'n'])
    return returnValue


def getJson(year=2014, month=1, day=1, newsType=0):
    if year == datetime.datetime.now().year and \
                    month == datetime.datetime.now().month and \
                    day == datetime.datetime.now().day:
        return networkExceptionCatch(getSiteURL(newsType)[2] + dateFormat(
            year, month, day) + '/0.js')
    else:
        return networkExceptionCatch(
            getSiteURL(newsType)[2] + dateFormat(year, month, day) + '/0.js')


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
        del tmp
        del text
        del tmpValue
        del childClassification
        del valuelist
        gc.collect()
    return returnValue


def sendToMongodb(insertData):
    db = MongoClient()
    collection = db.client['neteasenews']['news']
    collection.insert_one(insertData)
    db.close()


def getnews(URL):
    date = str()
    html = networkExceptionCatch(URL)
    soup = BeautifulSoup(html, 'html.parser')
    alls = soup.find_all('div', id="endText")
    for div in alls:
        if div.find('script'):
            div = re.sub(r'<script.*?</script>', '', div)
        p_in_div = div.find_all('p')
        if len(p_in_div) is 0:
            p_in_div = re.sub(r'(<div id="endText">)(.*?)(</p>)(<p>)', r'\1\2\4', p_in_div)
        for p_tag in p_in_div:
            if p_tag.text is not None:
                date += p_tag.text + u'\n'
    return date


def childProcess(year=2014, month=1, day=1, newsType=0):
    jsonlist = jsonFormat(year=year, month=month, day=day, newsType=newsType)
    if len(jsonlist) is not 0:
        for items in jsonlist:
            sendToMongodb(
                {'date': items[0], 'time': items[1], 'class': items[2], 'childclass': items[3],
                 'url': items[4], 'title': items[5], 'content': getnews(str(items[4]))})
            gc.collect()
        del jsonlist
        gc.collect()


# 网易的接口最多只能获取到2014年3月22日的新闻。再往前也有对应的接口，不过已经无法工作
# 如果改用腾讯的接口，虽然能获取到2009年1月1日的新闻，但网页处理方面比较麻烦（主要是腾讯的网页改过版），放弃
def main(startyear=2014, startmonth=1, startday=1, startnewsType=0):
    for year in range(2014, datetime.datetime.now().year + 1):
        if year < startyear:
            continue
        for month in range(1, 13):
            if month < startmonth:
                continue
            for day in range(1, calendar.monthrange(year, month)[1] + 1):
                if day < startday:
                    continue
                pool = multiprocessing.Pool()
                for newsType in range(0, 7):
                    if newsType < startnewsType:
                        continue
                    pool.apply_async(childProcess, args=(year, month, day, newsType))
                pool.close()
                pool.join()
                gc.collect()

## TODO:程序崩溃时保留状态，以便恢复
# def restoreProcess():


## TODO:从上次的状态中恢复
# def recoveryFromCrash():


if __name__ == '__main__':
    main()
