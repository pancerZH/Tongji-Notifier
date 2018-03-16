import sqlite3


def act_with_database(note_dict):
    conn = sqlite3.connect('TJ_notice.db')
    cursor = conn.cursor()
    cursor.execute('create table notice (id varchar(10) primary key, title varchar(100))')
    cursor.close()
    conn.commit()
    conn.close()