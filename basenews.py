from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
from selenium import webdriver
import time
import requests
URL = 'http://news.163.com/17/0411/22/CHPC96CE0001875O.html'
date=[]
html=requests.get(URL)

soup=BeautifulSoup(html.text)
all=soup.find(id="endText")
subject=all.find('p',{'class':"otitle"})
print(subject)
for p in all.find_all('p'):
    print(p)
