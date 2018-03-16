import requests
import re
import sqlite3
from bs4 import BeautifulSoup


def login(username,password,header,s):

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
    conn = sqlite3.connect('TJ_notice.db')
    cursor = conn.cursor()
    for key in note_dict:
        content = note_dict[key]
        cursor.execute('select * from notice where id=?', (key,))
        result = cursor.fetchall()
        if len(result) == 0:  # 未查询到结果
            cursor.execute('insert into notice (id, title) values (?, ?)', (key, content))
            print('insert one tuple : {}'.format(key))
        else:
            print(result)
    cursor.close()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    header={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}
    s=requests.session()
    login('1551719','108243',header,s)
    note_dict = get_table(header,s)
    act_with_database(note_dict)