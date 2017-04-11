import calendar
import datetime
import json

import re
import requests


def getJson(year=1970, month=1, day=1):
    if year == datetime.datetime.now().year and \
                    month == datetime.datetime.now().month and \
                    day == datetime.datetime.now().day:
        r = requests.get('http://news.163.com/specical/0001220O/news_json.js')
        r.encoding = 'gbk'
    else:
        r = requests.get(
            'http://snapshot.news.163.com/wgethtml/http+!!news.163.com!special!0001220O!news_json.js/' + dateFormat(
                year, month, day) + '/0.js')
    return r.text


def dateFormat(year=1970, month=1, day=1):
    dateString = datetime.date(year, month, day).isoformat().split('-')
    return dateString[0] + '-' + dateString[1] + '/' + dateString[2]


def jsonFormat(year=1970, month=1, day=1):
    text = getJson(year, month, day)
    returnValue = list()
    if text.startwith('var data=') is False:
        returnValue = list()
    else:
        tmp = re.sub(',*,', ',', text.lstrip('var data=').rstrip(';').replace('\n', '').replace(',[]', ''))
        tmpValue = json.loads(tmp)
        for list0 in tmpValue[u'news']:
            for list1 in list0:
                returnValue = list().append(
                    (list1[u'p'].split()[0], list1[u'p'].split()[1], list1[u'c'], list1[u'l'], list1[u't']))

    return returnValue


itemlist = list()

for year in range(1970, datetime.datetime.now().year):
    for month in range(1, 12):
        for day in range(1, calendar.monthrange(year, month)):
            tmplist = jsonFormat(year, month, day)
            if tmplist is None:
                continue
            else:
                for items in tmplist:
                    itemlist.append(items)
