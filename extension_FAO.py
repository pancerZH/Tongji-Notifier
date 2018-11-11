# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import env_build
import general_operation as go


def get_FAO(s):
    """ 获取第一页通知id和标题 """
    FAO_url = 'https://fao.tongji.edu.cn/4111/list.htm'
    res = s.get(FAO_url)
    soup = BeautifulSoup(res.content, 'html.parser')
    noticeLink_title = {}
    for notice in soup.find_all(href=re.compile('c4111a')):
        notice_id = notice['href']
        noticeLink_title[notice_id] = notice['title'].encode('gbk', 'ignore').decode('gbk')

    return noticeLink_title


def clean_id(noticeLink_title):
    """ 将url转为id """
    notice_title = {}
    for link in noticeLink_title:
        notice_id = 'FAO' + link.split('/')[3][6:]
        notice_title[notice_id] = noticeLink_title[link]

    return notice_title


def recover_url(ori_notice_list, noticeLink_title, s):
    notice_list = []
    for link in noticeLink_title:
        notice_id = 'FAO' + link.split('/')[3][6:]
        if notice_id in ori_notice_list:
            notice_list.append(link)

    return notice_list


def get_FAO_detail(notice_list, s):
    """ 爬取详细信息 """
    detail_dict = {}
    for ids in notice_list:
        detail_url = 'https://fao.tongji.edu.cn'
        detail_url = detail_url + ids
        res = s.get(detail_url)
        soup = BeautifulSoup(res.content, 'html.parser')
        article = soup.find_all('div', attrs={'class': 'wp_articlecontent'})
        article = BeautifulSoup(str(article), 'lxml')
        detail = ''
        for line in article.find_all('p'):
            detail += (line.get_text() + '\n')

        detail_dict[ids] = detail

    return detail_dict


def get_FAO_run():
    """ 获取外事办通知的整个流程 """
    s = requests.session()
    noticeLink_title_dict = get_FAO(s)
    notice_title_dict = clean_id(noticeLink_title_dict)
    ori_notice_list = go.act_with_database(notice_title_dict)
    notice_list = recover_url(ori_notice_list, noticeLink_title_dict, s)
    detail_dict = get_FAO_detail(notice_list, s)
    go.send_to_user(noticeLink_title_dict, detail_dict)


def deploy_FAO():
    """ 部署 """
    s = requests.session()
    noticeLink_title_dict = get_FAO(s)
    notice_title_dict = clean_id(noticeLink_title_dict)
    go.act_with_database(notice_title_dict)


if __name__ == '__main__':
    get_FAO_run()