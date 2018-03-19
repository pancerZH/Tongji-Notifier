# -*- coding:utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header

def sendMail(sender,password,tolist,subject,body):

    server='smtp.qq.com'
    port=587

    mBody=MIMEText(body,'plain','gbk')
    subject = Header(subject, 'utf-8').encode()

    header='To:'+';'.join(tolist)+'\n'
    header=header+'From:'+sender+'\n'
    header=header+'Subject:'+subject+'\n'
    message=header+mBody.as_string()
 
    smtpserver=smtplib.SMTP(server,port)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(sender,password)
    smtpserver.sendmail(sender,tolist,message)
    smtpserver.quit()