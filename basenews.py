#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import requests
from bs4 import BeautifulSoup


def getanews(URL):
    date = list()
    html = requests.get(URL)
    soup = BeautifulSoup(html.text, 'html.parser')
    all = soup.find(id="endText")
    subject_tag = all.find('p', {'class': "otitle"})
    del subject_tag['class']
    for p_tag in all.find_all(re.compile("p")):
        if (not p_tag.has_attr('class')):
            date.append(str(p_tag))
            print(str(p_tag))
    return date


# 调试用，完成后移除
if __name__ == '__main__':
    getanews('http://ent.163.com/17/0413/21/CHUBHJ7C00038FO9.html')
