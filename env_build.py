# -*- coding:utf-8 -*-

import sqlite3
import time


def create_database():
    conn = sqlite3.connect('TJ_notice.db')
    cursor = conn.cursor()
    cursor.execute('create table notice (id varchar(10) primary key, title varchar(100))')
    cursor.execute('create table user (mail varchar(100) primary key)')
    cursor.close()
    conn.commit()
    conn.close()
    print('successfully build a database!')

    write_to_log('create database')


def create_TJID():
    with open('TJ','w') as fp:
        ids = input('please input your student ID:')
        password = input('please input your ID password:')
        fp.write(ids)
        fp.write('\n')
        fp.write(password)
        fp.close()

    write_to_log('create student ID record')


def create_mail():
    with open('mail','w') as fp:
        mail_address = input('please input your email address:')
        password = input('please input your email password:')
        fp.write(mail_address)
        fp.write('\n')
        fp.write(password)
        fp.close()

    write_to_log('create mail record')


def create_log():
    with open('notifier.log','w') as fp:
        str1 = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        fp.write('{} : create log\n'.format(str1))
        fp.close()


def write_to_log(content):
    with open('notifier.log','a') as fp:
        str1 = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        fp.write('{} : {}\n\n'.format(str1,content))
        fp.close()