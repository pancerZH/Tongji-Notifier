import sqlite3
import env_build
import re
import os

print('add : add a record to table user\tdelete : delete a record from table user')
print('show : show all records in table user\tquit : quit the program')
if os.path.exists('TJ_notice.db') == False:
    print('no database exists,please create one:')
    env_build.create_database()
conn = sqlite3.connect('TJ_notice.db')
cursor = conn.cursor()

while True:
    query = input('action : ')
    if re.match('^add\s',query):
        query = query[3:].replace(' ','')
        try:
            cursor.execute('insert into user (mail) values (?)',(query,))
            conn.commit()
        except:
            print('command add failed,perhaps there is already a record of {} in the table'.format(query))
    elif re.match('^delete\s',query):
        query = query[6:].replace(' ','')
        try:
            cursor.execute('delete from user where mail = (?)',(query,))
            conn.commit()
        except:
            print('command delete failed,perhaps {} not exist in the table'.format(query))
    elif re.match('^show',query) or re.match('^show$',query):
        try:
            res = cursor.execute('select * from user').fetchall()
            for address in res:
                print(address)
        except:
            print('unknown error in command show')
    elif re.match('^quit\s',query) or re.match('^quit$',query):
        break
    else:
        print('unknown command!')

cursor.close()
conn.commit()
conn.close()