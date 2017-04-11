from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
from selenium import webdriver
import time
import requests
#DURL = 'http://news.163.com/17/0412/10/CHQK5NN800018AOQ.html'

def getanews(URL):
    date=list()
    html=requests.get(URL)
    soup=BeautifulSoup(html.text)
    all=soup.find(id="endText")
    subject_tag=all.find('p',{'class':"otitle"})
    del subject_tag['class']
    for p_tag in all.find_all(re.compile("p")):
        if(not p_tag.has_attr('class')):
            date.append(str(p_tag))
            #print(str(p_tag))
    return date

