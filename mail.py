# -*- coding:utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header

def sendMail(sender,password,to,subject,body):

    server='smtp.qq.com'
    port=587

    tolist=to.split(',')
    mBody=MIMEText(body,'plain','gbk')
    subject = Header(subject, 'utf-8').encode()

    header='To:'+to+'\n'
    header=header+'From:'+sender+'\n'
    header=header+'Subject:'+subject+'\n'
    message=header+mBody.as_string()
 
    try:
        smtpserver=smtplib.SMTP(server,port)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo()
        smtpserver.login(sender,password)
        smtpserver.sendmail(sender,tolist,message)
        print('succeeded to send a mail')
    except smtplib.SMTPException:
        print('failed to send a mail')
    smtpserver.quit()