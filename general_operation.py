# -*- coding:utf-8 -*-

import sqlite3
import env_build
import mail


def act_with_database(note_dict):
    """ 连接数据库并查询通知 """
    """ 参数是一个id-标题的字典，返回值是包含所有新通知id的list """
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
            env_build.write_to_log('find new notification: {}'.format(note_dict[key]))

    cursor.close()
    conn.commit()
    conn.close()

    return notice_list


def send_to_user(note_dict, detail_dict):
    """ 向每个用户发送通知邮件 """
    """ note_dict是一个id-标题的字典，detail_dict是一个id-正文的字典 """
    conn = sqlite3.connect('TJ_notice.db')
    cursor = conn.cursor()
    cursor.execute('select * from user')
    result = cursor.fetchall()
    with open('mail','r') as fp:
        host_address = fp.readline().strip('\n')
        password = fp.readline().strip('\n')

    for key in detail_dict:
        title = '【TJ_notifier】' + note_dict[key]
        body = detail_dict[key]
        mail_list = []
        for mail_address in result:
            mail_list.append(mail_address[0])

        try:
            mail.sendMail(host_address,password,mail_list,title, body)
            env_build.write_to_log('send a mail to {}'.format(mail_list))
        except:
            env_build.write_to_log('failed to send a mail to {}'.format(mail_list))

    cursor.close()
    conn.commit()
    conn.close()