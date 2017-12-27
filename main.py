#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import warnings
import getpass
import datetime
import time
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import re


# 需要额外安装requests模块（Terminal执行"pip3 install requests"）


class SeatKiller(object):

    def __init__(self, token, username, password):
        self.login_url = 'https://seat.lib.whu.edu.cn:8443/rest/auth'  # 图书馆移动端登陆API
        self.usr_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/user'  # 用户信息API
        self.filters_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/free/filters'  # 分馆和区域信息API
        self.stats_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/room/stats2/'  # 单一分馆区域信息API（拼接buildingId）
        self.layout_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/room/layoutByDate/'  # 单一区域座位信息API（拼接roomId+date）
        self.search_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/searchSeats/'  # 空位检索API（拼接date+startTime+endTime）
        self.book_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/freeBook'  # 座位预约API

        # 已预先爬取的roomId
        self.xt = ['6', '7', '8', '9', '10', '11', '12', '4', '5']
        self.gt = ['19', '29', '31', '32', '33', '34', '35', '37', '38']
        self.yt = ['20', '21', '23', '24', '26', '27']
        self.zt = ['39', '40', '51', '52', '56', '59', '60', '61', '62', '65', '66']

        self.freeSeats = []  # 用于储存空闲seatId的数组
        self.token = token
        self.username = username
        self.password = password
        self.name = 'user'
        self.to_addr = False
        self.headers = {'Host': 'seat.lib.whu.edu.cn:8443',
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'Connection': 'keep-alive',
                        'Accept': '*/*',
                        'User-Agent': 'doSingle/11 CFNetwork/893.14.2 Darwin/17.3.0',
                        'Accept-Language': 'zh-cn',
                        'token': self.token,
                        'Accept-Encoding': 'gzip, deflate'}

    # 暂停程序运行至指定时间，无返回值
    def Wait(self, hour, minute, second):
        time_run = datetime.datetime.replace(datetime.datetime.now(), hour=hour, minute=minute, second=second)
        delta = time_run - datetime.datetime.now()
        print('\n正在等待系统开放...剩余' + str(delta.seconds) + '秒')
        time.sleep(delta.seconds)

    # 发起GET请求，用旧token换取新token（旧token通过移动端抓包获得，可以保存后多次使用）并构建Headers，成功则返回token字符串，否则返回False
    def GetToken(self):
        datas = {'username': self.username, 'password': self.password}
        response = requests.get(self.login_url, params=datas, headers=self.headers, verify=False)
        try:
            json = response.json()
            print('\nTry getting token...Status: ' + str(json['status']))
            if json['status'] == 'success':
                self.token = json['data']['token']
                self.headers['token'] = self.token
                print('token：' + json['data']['token'])
                return json['data']['token']
            else:
                if json['code'] == '13':
                    print('登录失败: 用户名或密码不正确')
                else:
                    print(json)
                return False
        except:
            print('\nTry getting token...Status: Connection lost')
            return False

    # 发起GET请求，获取用户信息并打印出来，成功则返回True，否则返回False
    def GetUsrInf(self):
        response = requests.get(self.usr_url, headers=self.headers, verify=False)
        try:
            json = response.json()
            if json['status'] == 'success':
                print('\n你好，' + json['data']['name'] + ' 上次登陆时间：' + json['data']['lastLogin'])
                self.name = json['data']['name']
                return True
            else:
                print('\nTry getting user information...Status: fail')
                return False
        except:
            print('\nTry getting user information...Status: Connection lost')
            return False

    # 发起GET请求，获取全校图书馆的分馆和区域信息，成功则返回json，否则返回False
    def GetBuildings(self):
        response = requests.get(self.filters_url, headers=self.headers, verify=False)
        try:
            json = response.json()
            print('\nTry getting building information...Status: ' + str(json['status']))
            if json['status'] == 'success':
                return json
            else:
                print(json)
                return False
        except:
            print('\nTry getting building information...Status: Connection lost')
            return False

    # 发起GET请求，获取当前某分馆各区域剩余的座位数，成功则返回json，否则返回False
    def GetRooms(self, buildingId):
        url = self.stats_url + buildingId
        response = requests.get(url, headers=self.headers, verify=False)
        try:
            json = response.json()
            print('\nTry getting room information...Status: ' + str(json['status']))
            if json['status'] == 'success':
                return json
            else:
                print(json)
                return False
        except:
            print('\nTry getting room information...Status: Connection lost')
            return False

    # 发起GET请求，获取当前某区域内的位置信息，成功则返回json，否则返回False
    def GetSeats(self, roomId):
        url = self.layout_url + roomId + '/' + date
        response = requests.get(url, headers=self.headers, verify=False)
        try:
            json = response.json()
            print('\nTry getting seat information...Status: ' + str(json['status']))
            if json['status'] == 'success':
                return json
            else:
                print(json)
                return False
        except:
            print('\nTry getting seat information...Status: Connection lost')
            return False

    # 发起GET请求，检索某区域内指定时间段的空位，成功则返回True并将seatId存入freeSeats数组中，否则返回False
    def SearchFreeSeat(self, buildingId, roomId, date, startTime, endTime, batch='9999', page='1'):
        url = self.search_url + date + '/' + startTime + '/' + endTime
        datas = {'t': '1', 'roomId': roomId, 'buildingId': buildingId, 'batch': batch, 'page': page, 't2': '2'}
        response = requests.post(url, headers=self.headers, data=datas, verify=False)
        try:
            json = response.json()
            if json['data']['seats'] != {}:
                print('\nTry searching for free seats in room ' + roomId + '...Status: success')
                for num in json['data']['seats']:
                    self.freeSeats.append(json['data']['seats'][num]['id'])
                return True
            else:
                print('\nTry searching for free seats in room ' + roomId + '...Status: failed')
                return False
        except:
            print('\nTry searching for free seats in room ' + roomId + '...Status: Connection lost')
            return False

    # 发起POST请求，尝试预定指定座位，成功则打印预定信息并返回'Success'，失败则返回'Fail'，连接丢失则返回'Connection lost'
    def BookSeat(self, seatId, date, startTime, endTime):
        datas = {'t': '1', 'startTime': startTime, 'endTime': endTime, 'seat': seatId, 'date': date, 't2': '2'}
        response = requests.post(self.book_url, headers=self.headers, data=datas, verify=False)
        try:
            json = response.json()
            print('\nTry booking seat...Status: ' + str(json['status']))
            if json['status'] == 'success':
                self.PrintBookInf(json)
                if SK.to_addr:
                    if self.SendMail(json):
                        print('\n\n邮件提醒已发送，若接收不到提醒，请将\'seatkiller@outlook.com\'添加至邮箱白名单')
                    else:
                        print('\n邮件发送失败')
                return 'Success'
            else:
                print(json)
                return 'Fail'
        except:
            print('\nTry booking seat...Status: Connection lost')
            return 'Connection lost'

    # 打印座位预约凭证
    def PrintBookInf(self, json):
        print('\n--------------------座位预约成功!--------------------')
        print('ID：' + str(json['data']['id']))
        print('凭证号码：' + json['data']['receipt'])
        print('时间：' + json['data']['onDate'] + ' ' + json['data']['begin'] + '～' + json['data']['end'])
        if json['data']['checkedIn']:
            print('状态：已签到')
        else:
            print('状态：预约')
        print('地址：' + json['data']['location'])
        print('---------------------------------------------------')

    # 邮件发送座位预约凭证
    def SendMail(self, json):
        try:
            # 设置SMTP服务器及账号密码
            from_addr = 'seatkiller@outlook.com'
            password = 'simplebutunique2018'
            smtp_server = 'smtp-mail.outlook.com'

            # 构造邮件正文
            text = '---------------------座位预约凭证----------------------' + '\nID：' + str(json['data']['id']) + '\n凭证号码：' + \
                   json['data']['receipt'] + '\n时间：' + json['data']['onDate'] + ' ' + json['data']['begin'] + '～' + \
                   json['data']['end']
            if json['data']['checkedIn']:
                text = text + '\n状态：已签到'
            else:
                text = text + '\n状态：预约'
            text = text + '\n地址：' + json['data'][
                'location'] + '\n-----------------------------------------------------\n\nPowered by goolhanrry'

            msg = MIMEText(text, 'plain', 'utf-8')
            msg['From'] = 'SeatKiller' + ' <' + from_addr + '>'
            msg['To'] = 'user' + ' <' + self.to_addr + '>'
            msg['Subject'] = Header('座位预约成功', 'utf-8').encode()

            # 发送邮件
            server = smtplib.SMTP(smtp_server, 587)
            server.set_debuglevel(1)
            server.starttls()
            server.login(from_addr, password)
            server.sendmail(from_addr, self.to_addr, msg.as_string())
            server.quit()
            return True
        except:
            return False


# ----------------------------自动运行脚本-------------------------------

if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    token = '75PLJJO8PV12084027'  # 预先移动端抓包获取

    username = input('请输入学号：')
    password = getpass.getpass('请输入图书馆密码：')

    SK = SeatKiller(token, username, password)

    if input('请输入抢座模式（1.自动 2.手动）：') == '1':
        buildingId = '1'
        roomId = '0'
        seatId = '7469'
        startTime = '480'
        endTime = '720'
        rooms = SK.xt
        SK.to_addr = '879316283@qq.com'
    else:
        buildingId = input('请输入分馆编号（1.信息科学分馆 2.工学分馆 3.医学分馆 4.总馆）：')
        if buildingId == '1':
            rooms = SK.xt
            roomId = input('已获取区域列表：4.一楼3C创客空间\n'
                           '             5.一楼创新学习讨论区\n'
                           '             6.二楼西自然科学图书借阅区\n'
                           '             7.二楼东自然科学图书借阅区\n'
                           '             8.三楼西社会科学图书借阅区\n'
                           '             9.四楼西图书阅览区\n'
                           '             10.三楼东社会科学图书借阅区\n'
                           '             11.四楼东图书阅览区\n'
                           '             12.三楼自主学习区\n'
                           '             14.3C创客-双屏电脑（20台）\n'
                           '             15.创新学习-MAC电脑（12台）\n'
                           '             16.创新学习-云桌面（42台）\n'
                           '请输入房间编号（若由系统自动选择请输入\'0\'）：')
        elif buildingId == '2':
            rooms = SK.gt
            roomId = input('已获取区域列表：19.201室-东部自科图书借阅区\n'
                           '             29.2楼-中部走廊\n'
                           '             31.205室-中部电子阅览室笔记本区\n'
                           '             32.301室-东部自科图书借阅区\n'
                           '             33.305室-中部自科图书借阅区\n'
                           '             34.401室-东部自科图书借阅区\n'
                           '             35.405室中部期刊阅览区\n'
                           '             37.501室-东部外文图书借阅区\n'
                           '             38.505室-中部自科图书借阅区\n'
                           '请输入区域编号（若由系统自动选择请输入\'0\'）：')
        elif buildingId == '3':
            rooms = SK.yt
            roomId = input('已获取区域列表：20.204教学参考书借阅区\n'
                           '             21.302中文科技图书借阅B区\n'
                           '             23.305科技期刊阅览区\n'
                           '             24.402中文文科图书借阅区\n'
                           '             26.502外文图书借阅区\n'
                           '             27.506医学人文阅览区\n'
                           '请输入房间编号（若由系统自动选择请输入\'0\'）：')
        elif buildingId == '4':
            rooms = SK.zt
            roomId = input('已获取区域列表：39.A1-座位区\n'
                           '             40.C1自习区\n'
                           '             51.A2\n'
                           '             52.A3\n'
                           '             56.B3\n'
                           '             59.B2\n'
                           '             60.A4\n'
                           '             61.A5\n'
                           '             62.A1-沙发区\n'
                           '             65.B1\n'
                           '             66.A1-苹果区\n'
                           '请输入房间编号（若由系统自动选择请输入\'0\'）：')
        else:
            print('分馆编号输入不合法，已默认设置为\'信息科学分馆\'，房间编号由系统自动选择')
            buildingId = '1'
            roomId = '0'

            if roomId == '0':
                seatId = '0'
            else:
                seatId = input('请输入座位ID（若由系统自动选择请输入\'0\'）：')

        startTime = input('请输入开始时间（以分钟为单位，从0点开始计算）：')
        endTime = input('请输入结束时间（以分钟为单位，从0点开始计算）：')
        SK.to_addr = input('请输入邮箱地址，抢座成功之后将发送邮件提醒（若不需要邮件提醒，此项可放空）：')
        mail_addr = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
        if re.match(mail_addr, SK.to_addr):
            print('\n邮箱地址正确，可以发送邮件提醒')
        else:
            print('\n邮箱地址有误，无法发送邮件提醒')
            SK.to_addr = False

    while True:
        SK.Wait(22, 14, 30)
        try_booking = True
        date = datetime.date.today()
        date = date.strftime('%Y-%m-%d')
        print('\ndate:' + date)

        if SK.GetToken():
            SK.GetUsrInf()
            SK.GetBuildings()
            SK.GetRooms(buildingId)
            if roomId != '0':
                SK.GetSeats(roomId)

            SK.Wait(22, 15, 0)
            while try_booking:
                if seatId != '0':
                    if SK.BookSeat(seatId, date, startTime, endTime) == 'Success':
                        try_booking = False
                    else:
                        print('\n指定座位预约失败，尝试全馆检索其他空位...')
                        seatId = '0'
                elif datetime.datetime.now() >= datetime.datetime.replace(datetime.datetime.now(), hour=23,
                                                                          minute=45, second=0):
                    print('\n抢座失败，座位预约系统已关闭，2小时后尝试捡漏')
                    # time.sleep(7200)
                    print('\n-------------------------捡漏模式开始-------------------------')
                    try_picking = True
                    date = datetime.date.today()
                    date = date.strftime('%Y-%m-%d')
                    while try_picking:
                        SK.freeSeats = []
                        if SK.GetToken():
                            for i in rooms:
                                SK.SearchFreeSeat(buildingId, i, date, startTime, endTime)
                            for freeSeatId in SK.freeSeats:
                                response = SK.BookSeat(freeSeatId, date, startTime, endTime)
                                if response == 'Success':
                                    try_picking = False
                                    break
                                elif response == 'Fail':
                                    time.sleep(5)
                                    continue
                                else:
                                    print('\n连接丢失，5分钟后尝试继续抢座')
                                    time.sleep(300)
                                    continue
                        time.sleep(5)
                        if datetime.datetime.now() >= datetime.datetime.replace(datetime.datetime.now(), hour=20,
                                                                                minute=0, second=0):
                            try_picking = False
                    print('\n-------------------------捡漏模式结束-------------------------')
                    try_booking = False
                else:
                    SK.freeSeats = []
                    if roomId == '0':
                        for i in rooms:
                            SK.SearchFreeSeat(buildingId, i, date, startTime, endTime)
                    else:
                        if SK.SearchFreeSeat(buildingId, roomId, date, startTime, endTime):
                            pass
                        else:
                            for i in rooms:
                                SK.SearchFreeSeat(buildingId, i, date, startTime, endTime)

                    for freeSeatId in SK.freeSeats:
                        response = SK.BookSeat(freeSeatId, date, startTime, endTime)
                        if response == 'Success':
                            try_booking = False
                            break
                        elif response == 'Fail':
                            time.sleep(3)
                            continue
                        else:
                            ddl = datetime.datetime.replace(datetime.datetime.now(), hour=23, minute=45, second=0)
                            delta = ddl - datetime.datetime.now()
                            print('\n连接丢失，一分钟后尝试重新抢座，系统开放时间剩余' + str(delta.seconds) + '秒\n')
                            time.sleep(60)
                            continue
            print('\n抢座运行结束')
            time.sleep(1800)
        else:
            break
