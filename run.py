# -*- coding:utf-8 -*-

import requests
import re
import sqlite3
from bs4 import BeautifulSoup
import os
import create_database
import mail


def login(username,password,header,s):
    '''登陆4m3'''
    startURL='http://4m3.tongji.edu.cn/eams/login.action'
    href='http://4m3.tongji.edu.cn/eams/samlCheck'
    res=s.get(startURL)
    header['Upgrade-Insecure-Requests']='1'
    res=s.get(href,headers=header)
    soup=BeautifulSoup(res.content,'html.parser')
    jumpURL=soup.meta['content'][6:]
    header['Accept-Encoding']='gzip, deflate, sdch, br'
    res=s.get(jumpURL,headers=header)

    soup=BeautifulSoup(res.content,'html.parser')
    logPageURL='https://ids.tongji.edu.cn:8443'+soup.form['action']
    res=s.get(logPageURL,headers=header)

    data={'option':'credential','Ecom_User_ID':username,'Ecom_Password':password,'submit':'登录'}
    soup=BeautifulSoup(res.content,'html.parser')
    loginURL=soup.form['action']
    res=s.post(loginURL,headers=header,data=data)

    soup=BeautifulSoup(res.content,'html.parser')
    str=soup.script.string
    str=str.replace('<!--',' ')
    str=str.replace('-->',' ')
    str=str.replace('top.location.href=\'',' ')
    str=str.replace('\';',' ')
    jumpPage2=str.strip()
    res=s.get(jumpPage2,headers=header)

    soup=BeautifulSoup(res.content,'html.parser')
    message={}
    messURL=soup.form['action']
    message['SAMLResponse']=soup.input['value']
    message['RelayState']=soup.input.next_sibling.next_sibling['value']
    res=s.post(messURL,headers=header,data=message)


def get_table(header, s):
    '''从4m3获取通知标题'''
    tableURL = 'http://4m3.tongji.edu.cn/eams/home!welcome.action'
    res=s.post(tableURL,headers=header)
    soup = BeautifulSoup(res.content,'html.parser')
    notice_dict = {}
    for ids in soup.find_all(onclick = re.compile('getNewNoticeInfo.*')):
        ori_str = ids['onclick']
        n_id = ori_str.split('\'')[1]
        notice_dict[n_id] = ids.string

    return notice_dict


def act_with_database(note_dict):
    '''连接数据库并查询通知'''
    conn = sqlite3.connect('TJ_notice.db')
    cursor = conn.cursor()
    notice_list = []
    for key in note_dict:
        content = note_dict[key]
        cursor.execute('select * from notice where id=?', (key,))
        result = cursor.fetchall()
        if len(result) == 0:  # 未查询到结果
            cursor.execute('insert into notice (id, title) values (?, ?)', (key, content))
            print('insert one tuple : {}'.format(key))
            notice_list.append(key)
        #else:
            #print(result)
    cursor.execute('delete from notice where id=?',('5917',))
    cursor.close()
    conn.commit()
    conn.close()

    return notice_list


def get_detail(header, s, notice_list):
    """ 获取每条新通知的详细内容 """
    detailURL = 'http://4m3.tongji.edu.cn/eams/noticeDocument!info.action?ifMain=1&notice.id='
    detail_dict = {}
    for noticeID in notice_list:
        oneURL = detailURL + noticeID
        res = s.get(oneURL, headers=header)
        soup=BeautifulSoup(res.content,'html.parser')
        notice_str = ''
        for ids in soup.find_all('span'):
            notice_str += ids.get_text()

        notice_str = notice_str.replace(' ','')
        notice_str = notice_str.replace('\xa0', '')
        notice_str = notice_str[0:int(len(notice_str)/2)]
        detail_dict[noticeID] = notice_str

    return detail_dict


def send_to_user(note_dict, detail_dict):
    """ 向每个用户发送通知邮件 """
    conn = sqlite3.connect('TJ_notice.db')
    cursor = conn.cursor()
    cursor.execute('select * from user')
    result = cursor.fetchall()
    try:
        pass_file = open('password.key','r')
    except:
        print('password file not exist!')
        exit(3)
    password = pass_file.readline()
    for key in detail_dict:
        title = '【TJ_notifier】' + note_dict[key]
        body = detail_dict[key]
        for mail_address in result:
            mail.sendMail('942740938@qq.com',password,mail_address[0],title, body)

    cursor.close()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    if os.path.exists('TJ_notice.db') == False:
        create_database.create_database()

    header={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}
    s=requests.session()
    login('1551719','108243',header,s)
    note_dict = get_table(header,s)
    notice_list = act_with_database(note_dict)
    detail_dict = get_detail(header,s,notice_list)
    send_to_user(note_dict,detail_dict)