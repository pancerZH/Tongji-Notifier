# -*- coding:utf-8 -*-

import requests
import re
from bs4 import BeautifulSoup
import os
import sys
import env_build
import datetime
import time
import general_operation as go
import extension_SSE as ex_SSE
import extension_FAO as ex_FAO


def login(header,s):
    '''登陆4m3'''
    with open('TJ','r') as fp:
        username = fp.readline().strip('\n')
        password = fp.readline().strip('\n')

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


def get_detail(header, s, notice_list):
    """ 获取每条新通知的详细内容 """
    detailURL = 'http://4m3.tongji.edu.cn/eams/noticeDocument!info.action?ifMain=1&notice.id='
    detail_dict = {}
    for noticeID in notice_list:
        oneURL = detailURL + noticeID
        res = s.get(oneURL, headers=header)
        soup=BeautifulSoup(res.content,'html.parser')
        notice_str = ''
        for ids in soup.find_all('p'):
            notice_str += ids.get_text()

        notice_str = notice_str[0:int(len(notice_str)/2)]
        detail_dict[noticeID] = notice_str

    return detail_dict


def deploy():
    """ 部署模式，不发送新通知，仅发送部署通知邮件 """
    print('deploying')
    header={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}

    if os.path.exists('notifier.log') == False:
        env_build.create_log()
    if os.path.exists('TJ_notice.db') == False:
        env_build.create_database()
    if os.path.exists('TJ') == False:
        env_build.create_TJID()
    if os.path.exists('mail') == False:
        env_build.create_mail()

    s=requests.session()
    try:
        login(header,s)
    except:
        env_build.write_to_log('failed to log in 4m3')
        exit(3)
    note_dict = get_table(header,s)
    notice_list = go.act_with_database(note_dict)
    get_detail(header,s,notice_list)
    ex_SSE.deploy_SSE()
    ex_FAO.deploy_FAO()
    go.send_to_user({'1':'deploy succeed'},{'1':'begin service...'})

    s.close()
    print('deploy succeed!')


def run_now():
    """ 立刻检查4m3并将新通知通过邮件发送，仅执行一次 """
    header={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}

    if os.path.exists('notifier.log') == False:
        env_build.create_log()
    if os.path.exists('TJ_notice.db') == False:
        env_build.create_database()
    if os.path.exists('TJ') == False:
        env_build.create_TJID()
    if os.path.exists('mail') == False:
        env_build.create_mail()

    s=requests.session()
    print('running...')
    try:
        login(header,s)
    except:
        env_build.write_to_log('failed to log in 4m3')
        exit(3)
    note_dict = get_table(header,s)
    notice_list = go.act_with_database(note_dict)
    detail_dict = get_detail(header,s,notice_list)
    go.send_to_user(note_dict,detail_dict)

    ex_SSE.get_SSE_run()
    ex_FAO.get_FAO_run()
    print('succeed!')


def run_service():
    """ 正常运行模式 """
    header={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}

    while True:
        if os.path.exists('notifier.log') == False:
            env_build.create_log()
        if os.path.exists('TJ_notice.db') == False:
            env_build.create_database()
        if os.path.exists('TJ') == False:
            env_build.create_TJID()
        if os.path.exists('mail') == False:
            env_build.create_mail()

        now_hour = datetime.datetime.utcnow().hour
        if now_hour is 4 or now_hour is 10:  # 北京时间12点和18点
            s=requests.session()
            try:
                login(header,s)
            except:
                env_build.write_to_log('failed to log in 4m3')
                exit(3)
            note_dict = get_table(header,s)
            notice_list = go.act_with_database(note_dict)
            detail_dict = get_detail(header,s,notice_list)
            go.send_to_user(note_dict,detail_dict)

            ex_SSE.get_SSE_run()
            ex_FAO.get_FAO_run()
            time.sleep(3700)
        else:
            time.sleep(100)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'deploy':
        deploy()
        run_service()
    elif len(sys.argv) > 1 and sys.argv[1] == 'now':
        run_now()
    else:
        run_service()