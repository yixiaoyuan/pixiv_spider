#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import os
import time
import pickle
import urllib
import urllib2
import requests
import cookielib
import threading
from bs4 import BeautifulSoup

class Pixiv(object):
    def __init__(self,pixiv_id,password):
        self.pixiv_id = pixiv_id
        self.password = password
        self.get_cookies_url = "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index"
        self.get_postkey_url = "https://accounts.pixiv.net/login?return_to=http%3A%2F%2Fwww.pixiv.net%2Franking.php%3Fmode%3Ddaily&source=pc&view_type=page"
        self.headers_base =  {
            'Referer': 'https://accounts.pixiv.net/login?return_to=http%3A%2F%2Fwww.pixiv.net%2Franking.php%3Fmode%3Ddaily&source=pc&view_type=page',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }

        self.headers_download = {
             "Accept-Language": "zh-CN,zh;q=0.8",
             "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
        }

        self.login_data = ({
            'pixiv_id': self.pixiv_id,
            'password': self.password,
            'captcha': '',
            'g_recaptcha_response': '',
            'post_key': '',
            'source': 'pc'
        })

    def login(self):
        s = requests.session()

        page = s.get(self.get_postkey_url,headers=self.headers_base)
        content = page.text.encode("utf-8")
        pattern = re.compile('(?<=<input type="hidden" name="post_key" value=")\w*(?=">)')
        item = re.findall(pattern, content)
        if not item:
            print ('postkey is not found')
            exit()
        post_key = str(item[0])

        self.login_data['post_key'] = post_key
        res = s.post(self.get_cookies_url,data=self.login_data)
        m_cookies = s.cookies
        with open ('cookie.txt', 'wb') as f:
            pickle.dump(m_cookies, f)



    class MyThread(threading.Thread):
        def __init__(self,pic_url,pic_name,headers):
            threading.Thread.__init__(self)
            self.url = pic_url
            self.filename = pic_name
            self.headers = headers
        def run(self):
            res = urllib2.Request(self.url,headers=self.headers)
            req = urllib2.urlopen(res)
            picture = req.read()
            filename = self.filename + '.png'
            with open(filename, 'wb') as f:
                f.write(picture)
                f.close()

    def get_pic_number_list(self,url):
        number_list =[]
        res = requests.get(url,cookies=load_cookies('cookie.txt'), headers=self.headers_base)
        # print(res.status_code)
        if res == None:
            print ("can't open the %s page" %(url))
            exit()
        page = res.text
        pattern_number = re.compile(r'</div></a><a href="(.*?)"><h1 class="title" title="(.*?)">.*?</h1></a>',re.S)
        result_number = re.findall(pattern_number, page)
        for item in result_number:
            url = 'http://www.pixiv.net' + str(item[0])
            number_list.append(url)
        return number_list

    def get_pic_url(self,pic_page_url):
        pic_url = ''
        pic_name = ''
        res = requests.get(pic_page_url,cookies=load_cookies('cookie.txt'),headers=self.headers_base)
        pic_page = res.text
        soup = BeautifulSoup(pic_page,"lxml")
        tags = soup.find_all("img", attrs={"class": "original-image"})
        for item in tags:
            pic_url = item['data-src']
            pic_name = item['alt']
        return pic_url,pic_name


    def download_pic(self,pic_page_url):
        pic_url, pic_name = self.get_pic_url(pic_page_url)
        if pic_url:                                                     # 若是单图
            self.headers_download['referer'] = pic_page_url
            name = pic_name
            mt = self.MyThread(pic_url,name,self.headers_download)
            mt.start()
            return pic_name
        else:
            return 'None'
def load_cookies(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

def save_cookies(requests_cookiejar, filename):
    with open(filename, 'wb') as f:
        pickle.dump(requests_cookiejar, f)


pixiv_id = ''
password = ''
base_fouce_url = 'http://www.pixiv.net/bookmark_new_illust.php'
number = 100
pixiv = Pixiv(pixiv_id,password)
pixiv.login()

Num = 1
for n in range(70,80):
    fouce_url = base_fouce_url + '?p=' + str(n)
    pic_number_list = pixiv.get_pic_number_list(fouce_url)
    for item in pic_number_list:
        try:
            filename = pixiv.download_pic(item)
            print (filename + ' the NO.%d   page%d')  %(Num,n)
        Num += 1
