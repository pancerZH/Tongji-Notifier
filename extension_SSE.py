# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import env_build
import general_operation as go


def get_SSE(s):
    """ 获取所有通知id和标题 """
    SSE_url = 'http://sse.tongji.edu.cn/Data/List/xwdt'
    res = s.get(SSE_url)
    soup=BeautifulSoup(res.content,'html.parser')
    notice_title = {}  # 第一个返回的字典 id-标题
    for notice in soup.find_all(href = re.compile('/Data/View/*')):
        ori_str = notice['href']
        notice_id = 'SSE'+ori_str.split('/')[3]
        notice_title[notice_id] = notice.get_text().strip()
    
    return notice_title


def get_SSE_detail(notice_list, s):
    """ 爬取详细信息 """
    detail_dict = {}
    for ids in notice_list:
        detail_url = 'http://sse.tongji.edu.cn/Data/View/'
        detail_url = detail_url+ids.strip('SSE')
        res = s.get(detail_url)
        soup = BeautifulSoup(res.content,'html.parser')
        detail = ''
        for line in soup.find_all('p'):
            detail += (line.get_text() + '\n')
    
        detail_dict[ids] = detail
        
    return detail_dict


def get_SSE_run():
    """ 获取软件学院通知的整个流程 """
    s=requests.session()
    notice_title_dict = get_SSE(s)
    notice_list = go.act_with_database(notice_title_dict)
    detail_dict = get_SSE_detail(notice_list,s)
    go.send_to_user(notice_title_dict,detail_dict,'软件学院')


def deploy_SSE():
    """ 部署 """
    s=requests.session()
    notice_title_dict = get_SSE(s)
    go.act_with_database(notice_title_dict)


if __name__ == '__main__':
    get_SSE_run()