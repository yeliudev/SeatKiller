#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import datetime
import time
import smtplib
from email.header import Header
from email.mime.text import MIMEText


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
        self.cancel_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/cancel/'  # 取消预约API

        # 已预先爬取的roomId
        self.xt = ['6', '7', '8', '9', '10', '11', '12', '4', '5']
        self.xt_less = ['6', '7', '8', '9', '10', '11', '12']
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
    def GetSeats(self, roomId, date):
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

    # 发起GET请求，检索某区域内指定时间段的空位，成功则返回'Success'并将seatId存入freeSeats数组中，否则返回'Failed'，连接丢失则返回'Connection lost'
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
                return 'Success'
            else:
                print('\nTry searching for free seats in room ' + roomId + '...Status: failed')
                return 'Failed'
        except:
            print('\nTry searching for free seats in room ' + roomId + '...Status: Connection lost')
            return 'Connection lost'

    # 发起POST请求，尝试预定指定座位，成功则打印预定信息并返回'Success'，失败则返回'Failed'，连接丢失则返回'Connection lost'
    def BookSeat(self, seatId, date, startTime, endTime):
        datas = {'t': '1', 'startTime': startTime, 'endTime': endTime, 'seat': seatId, 'date': date, 't2': '2'}
        response = requests.post(self.book_url, headers=self.headers, data=datas, verify=False)
        try:
            json = response.json()
            print('\nTry booking seat...Status: ' + str(json['status']))
            if json['status'] == 'success':
                self.PrintBookInf(json)
                if self.to_addr:
                    if self.SendMail(json):
                        print('\n\n邮件提醒已发送，若接收不到提醒，请将\'seatkiller@outlook.com\'添加至邮箱白名单')
                    else:
                        print('\n邮件发送失败')
                if json['data']['location'][12] == '3':
                    return str(json['data']['id'])
                else:
                    return 'Success'
            else:
                print(json)
                return 'Failed'
        except:
            print('\nTry booking seat...Status: Connection lost')
            return 'Connection lost'

    # 发起GET请求，取消指定id的座位预约，成功则返回True，否则返回False
    def CancelReservation(self, id):
        url = self.cancel_url + id
        response = requests.get(url, headers=self.headers, verify=False)
        try:
            json = response.json()
            print('\nTry cancelling reservation...Status: ' + str(json['status']))
            if json['status'] == 'success':
                return True
            else:
                print(json)
                return False
        except:
            print('\nTry getting seat information...Status: Connection lost')
            return False

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

    # 捡漏模式
    def Loop(self, buildingId, rooms, startTime, endTime):
        print('\n-------------------------捡漏模式开始--------------------------')
        date = datetime.date.today()
        date = date.strftime('%Y-%m-%d')
        while True:
            self.freeSeats = []
            if self.GetToken():
                for i in rooms:
                    if self.SearchFreeSeat(buildingId, i, date, startTime, endTime) == 'Connection lost':
                        print('\n连接丢失，1分钟后尝试继续检索空位')
                        time.sleep(60)
                for freeSeatId in self.freeSeats:
                    response = self.BookSeat(freeSeatId, date, startTime, endTime)
                    if response[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or response == 'Success':
                        print('\n捡漏成功')
                        print('\n-------------------------捡漏模式结束--------------------------')
                        return response
                    elif response == 'Failed':
                        time.sleep(3)
                        continue
                    else:
                        print('\n连接丢失，5分钟后尝试继续抢座')
                        time.sleep(300)
                        continue
                else:
                    ddl = datetime.datetime.replace(datetime.datetime.now(), hour=19, minute=0, second=0)
                    delta = ddl - datetime.datetime.now()
                    print('\n循环结束，5秒后进入下一个循环，运行时间剩余' + str(delta.seconds) + '秒\n')
                    time.sleep(5)
            else:
                print('\n获取token失败，5分钟后再次尝试')
                time.sleep(300)

            if datetime.datetime.now() >= datetime.datetime.replace(datetime.datetime.now(), hour=20,
                                                                    minute=0, second=0):
                print('\n捡漏失败，超出运行时间')
                print('\n-------------------------捡漏模式结束--------------------------')
                return False

    # 换座模式（限信息科学分馆）
    def ExchangeLoop(self, buildingId, startTime, endTime, id):
        print('\n-------------------------换座模式开始--------------------------')
        date = datetime.date.today()
        date = date.strftime('%Y-%m-%d')
        cancel = False
        cancelled = False
        while True:
            self.freeSeats = []
            if self.GetToken():
                for i in self.xt_less:
                    res = self.SearchFreeSeat(buildingId, i, date, startTime, endTime)
                    if res == 'Success' and not cancelled:
                        cancel = True
                    elif res == 'Connection lost':
                        print('\n连接丢失，1分钟后尝试继续检索空位')
                        time.sleep(60)
                if cancel:
                    cancel = False
                    if self.CancelReservation(id):
                        cancelled = True
                for freeSeatId in self.freeSeats:
                    response = self.BookSeat(freeSeatId, date, startTime, endTime)
                    if response == 'Success':
                        print('\n换座成功')
                        print('\n-------------------------换座模式结束--------------------------')
                        return True
                    elif response == 'Failed':
                        time.sleep(3)
                        continue
                    else:
                        print('\n连接丢失，5分钟后尝试继续抢座')
                        time.sleep(300)
                        continue
                else:
                    ddl = datetime.datetime.replace(datetime.datetime.now(), hour=19, minute=0, second=0)
                    delta = ddl - datetime.datetime.now()
                    print('\n循环结束，10秒后进入下一个循环，运行时间剩余' + str(delta.seconds) + '秒\n')
                    time.sleep(10)
            else:
                print('\n获取token失败，5分钟后再次尝试')
                time.sleep(300)

            if datetime.datetime.now() >= datetime.datetime.replace(datetime.datetime.now(), hour=20,
                                                                    minute=30, second=0):
                if cancelled:
                    print('\n换座失败，原座位已丢失')
                else:
                    print('\n换座失败，原座位未丢失')
                print('\n-------------------------换座模式结束--------------------------')
                return False
