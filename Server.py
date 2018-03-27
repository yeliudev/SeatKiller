#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import smtplib
import threading
import time
from email.header import Header
from email.mime.text import MIMEText


# 发起get请求，尝试发送邮件提醒
def SendMail(json, to_addr, passwd):
    try:
        # 设置SMTP服务器及账号密码
        from_addr = 'seatkiller@outlook.com'
        smtp_server = 'smtp-mail.outlook.com'

        # 构造邮件正文
        text = '---------------------座位预约凭证----------------------' + '\nID：' + str(json['data']['id']) + '\n凭证号码：' + \
               json['data']['receipt'] + '\n时间：' + json['data']['onDate'] + ' ' + json['data'][
                   'begin'] + '～' + \
               json['data']['end']
        if json['data']['checkedIn']:
            text = text + '\n状态：已签到'
        else:
            text = text + '\n状态：预约'
        text = text + '\n地址：' + json['data'][
            'location'] + '\n-----------------------------------------------------\n\nDesighed by goolhanrry from WHU'

        msg = MIMEText(text, 'plain', 'utf-8')
        msg['From'] = 'SeatKiller' + ' <' + from_addr + '>'
        msg['To'] = 'user' + ' <' + to_addr + '>'
        msg['Subject'] = Header('座位预约成功', 'utf-8').encode()

        # 发送邮件
        server = smtplib.SMTP(smtp_server, 587)
        server.set_debuglevel(1)
        server.starttls()
        server.login(from_addr, passwd)
        server.sendmail(from_addr, to_addr, msg.as_string())
        server.quit()
        return True
    except:
        return False


# TCP连接处理
def tcplink(sock, addr, passwd):
    try:
        print('\nAccept new connection from %s:%s...' % addr)
        sock.send('Hello'.encode('utf-8'))
        while True:
            data = sock.recv(1024)
            time.sleep(1)

            if not data or str(data.decode('utf-8')) == 'exit':
                break

            if str(data.decode('utf-8')) == 'SendMail':
                if SendMail(json, to_addr, passwd):
                    sock.send('success'.encode('utf-8'))
                    print('\nMail Sent Successfully')
                else:
                    sock.send('fail'.encode('utf-8'))
                    print('\nFailed')
            elif data.decode('utf-8')[0:4] == 'json':
                decodedData = data.decode('utf-8')[4:].replace(': ', ':').replace(':', ': ').replace('false', 'False')
                print('\ndecodedData: ' + decodedData)
                json = eval(decodedData)
                sock.send('Get json file...'.encode('utf-8'))
            else:
                to_addr = data.decode('utf-8')
                print('\nTo: ' + data.decode('utf-8') + '\n')
                sock.send('Get email address...'.encode('utf-8'))

        sock.close()
        print('Connection from %s:%s closed.' % addr)
    except:
        print('Connection from %s:%s lost.' % addr)
        pass


passwd = input('Passwd:')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 5210))
s.listen(10)
print('Waiting for connection...')

while True:
    sock, addr = s.accept()
    t = threading.Thread(target=tcplink, args=(sock, addr, passwd))
    t.start()
