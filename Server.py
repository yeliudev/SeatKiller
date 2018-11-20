# -*- coding: utf-8 -*-

import pymysql
import socket
import smtplib
import threading
import datetime
import time
from email.header import Header
from email.mime.text import MIMEText


FROM_ADDR = 'seatkiller@outlook.com'
SMTP_SERVER = 'smtp-mail.outlook.com'
DB_SERVER = '127.0.0.1'

sql_insert = "insert into user(username,nickname,version,lastLoginTime) values('%s','%s','%s','%s');"
sql_select = "select 1 from user where username='%s' limit 1;"
sql_update = "update user set version='%s',lastLoginTime='%s' where username='%s';"


def sendMail(data, to_addr, passwd):
    try:
        body = '---------------------座位预约凭证----------------------'
        body += '\nID：%d' % data['id']
        body += '\n凭证号码：%s' % data['receipt']
        body += '\n时间：%s %s～%s' % (data['onDate'], data['begin'], data['end'])
        body += '\n状态：%s' % ('已签到' if data['checkedIn'] else '预约')
        body += '\n地址：%s' % data['location']
        body += '\n-----------------------------------------------------'
        body += '\n\nBrought to you by goolhanrry😉'

        msg = MIMEText(body, 'plain', 'utf-8')
        msg['From'] = 'SeatKiller <%s>' % FROM_ADDR
        msg['To'] = 'user <%s>' % to_addr
        msg['Subject'] = Header('座位预约成功', 'utf-8').encode()

        server = smtplib.SMTP(SMTP_SERVER, 587)
        server.starttls()
        server.login(FROM_ADDR, passwd)
        server.sendmail(FROM_ADDR, to_addr, msg.as_string())
        server.quit()

        return True
    except:
        return False


def tcplink(sock, addr, passwd):
    try:
        # print('\nAccept new connection from %s:%s...' % addr)
        sock.send('hello'.encode())

        while True:
            data = sock.recv(512).decode()
            info = data.split()
            time.sleep(1)

            if info[0] == 'login':
                username = info[1]
                nickname = info[2]
                version = info[3]

                timeStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print('\n%s: %s %s (%s) logged in' % (timeStr, username, nickname, version))

                try:
                    cur.execute(sql_select % (username))
                    res = cur.fetchall()
                    if len(res):
                        cur.execute(sql_update % (version, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username))
                        db.commit()
                    else:
                        cur.execute(sql_insert % (username, nickname, version, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        db.commit()
                except:
                    print('Database update error')
                    db.rollback()

                break
            elif info[0] == 'json':
                json = eval(data[5:])
                print('\n' + json)
                print('\nSending mail to %s...' % json['to_addr'], end='')

                if sendMail(json['data'], json['to_addr'], passwd):
                    sock.send('success'.encode())
                    print('success')
                else:
                    sock.send('fail'.encode())
                    print('failed')

                break
            else:
                print('\nFormat error: ' + data)
                break

        sock.close()
        # print('Connection from %s:%s closed.' % addr)
    except:
        print('\nConnection from %s:%s lost.' % addr)


passwd = input('Passwd:')
dbPasswd = input('Database passwd:')

db = pymysql.connect(DB_SERVER, 'root', dbPasswd, 'user')
cur = db.cursor()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 5210))
s.listen(10)
print('Waiting for connection...')

while True:
    sock, addr = s.accept()
    t = threading.Thread(target=tcplink, args=(sock, addr, passwd))
    t.start()
