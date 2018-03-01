#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import datetime
import time
import sys
import random
import socket


# 需要额外安装requests模块（Terminal执行"pip3 install requests"）

class SeatKiller(object):

    def __init__(self, username='', password=''):
        self.login_url = 'https://seat.lib.whu.edu.cn:8443/rest/auth'  # 图书馆移动端登陆API
        self.usr_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/user'  # 用户信息API
        self.filters_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/free/filters'  # 分馆和区域信息API
        self.stats_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/room/stats2/'  # 单一分馆区域信息API（拼接buildingId）
        self.layout_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/room/layoutByDate/'  # 单一区域座位信息API（拼接roomId+date）
        self.search_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/searchSeats/'  # 空位检索API（拼接date+startTime+endTime）
        self.history_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/history/1/'  # 预约历史记录API（拼接历史记录个数）
        self.book_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/freeBook'  # 座位预约API
        self.cancel_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/cancel/'  # 取消预约API（拼接预约ID）
        self.stop_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/stop'  # 座位释放API

        # 已预先爬取的roomId
        self.xt = ('6', '7', '8', '9', '10', '11', '12', '16', '4', '5', '14', '15')
        self.xt_less = ('6', '7', '8', '9', '10', '11', '12', '16')
        self.gt = ('19', '29', '31', '32', '33', '34', '35', '37', '38')
        self.yt = ('20', '21', '23', '24', '26', '27')
        self.zt = ('39', '40', '51', '52', '56', '59', '60', '61', '62', '65', '66')

        self.allSeats = {}  # 用于储存某区域的所有座位信息
        self.freeSeats = []  # 用于储存空闲seatId的数组
        self.token = ''
        self.username = username
        self.password = password
        self.to_addr = ''
        self.headers = {'Host': 'seat.lib.whu.edu.cn:8443',
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'Connection': 'keep-alive',
                        'Accept': '*/*',
                        'User-Agent': 'doSingle/11 CFNetwork/893.14.2 Darwin/17.3.0',
                        'Accept-Language': 'zh-cn',
                        'token': self.token,
                        'Accept-Encoding': 'gzip, deflate'}
        self.state = {'RESERVE': '预约', 'CHECK_IN': '履约中', 'AWAY': '暂离'}

    # 暂停程序至指定时间，无返回值
    def Wait(self, hour, minute, second, nextDay=False):
        if nextDay:
            time_run = datetime.datetime.replace(datetime.datetime.now() + datetime.timedelta(days=1), hour=hour,
                                                 minute=minute, second=second)
        else:
            time_run = datetime.datetime.replace(datetime.datetime.now(), hour=hour, minute=minute, second=second)
        print('\n', end='')
        while True:
            delta = time_run - datetime.datetime.now()
            print('\r正在等待系统开放...剩余' + str(delta.total_seconds()) + '秒    ', end='')
            if delta.total_seconds() <= 0:
                break

    # 发起GET请求，用旧token换取新token（旧token通过移动端抓包获得，可以保存后多次使用）并构建Headers，成功则返回token字符串，否则返回False
    def GetToken(self):
        datas = {'username': self.username, 'password': self.password}
        print('\nTry getting token...Status: ', end='')
        try:
            response = requests.get(self.login_url, params=datas, headers=self.headers, verify=False)
            json = response.json()
            print(str(json['status']))
            if json['status'] == 'success':
                self.token = json['data']['token']
                self.headers['token'] = self.token
                print('token：' + json['data']['token'])
                return json['data']['token']
            else:
                print(json['message'])
                return False
        except:
            print('Connection lost')
            return False

    # 发起GET请求，获取用户信息并打印出来，成功则返回True，否则返回False
    def GetUsrInf(self):
        try:
            response = requests.get(self.usr_url, headers=self.headers, verify=False)
            json = response.json()
            if json['status'] == 'success':
                print('\n你好，' + json['data']['name'] + ' 上次登陆时间：' + json['data']['lastLogin'].replace('T', ' ')
                      .rstrip('.000') + ' 状态：' +
                      ('已进入' + json['data']['lastInBuildingName'] + ' 入馆时间：' + json['data']['lastIn'] if json['data'][
                          'checkedIn'] else '未入馆') + ' 违约记录：' + str(json['data']['violationCount']) + '次')
                return True
            else:
                print('\nTry getting user information...Status: failed')
                return False
        except:
            print('\nTry getting user information...Status: Connection lost')
            return False

    # 发起GET请求，获取全校图书馆的分馆和区域信息，成功则返回json，否则返回False
    def GetBuildings(self):
        print('\nTry getting building information...Status: ', end='')
        try:
            response = requests.get(self.filters_url, headers=self.headers, verify=False)
            json = response.json()
            print(str(json['status']))
            if json['status'] == 'success':
                return json
            else:
                print(json)
                return False
        except:
            print('Connection lost')
            return False

    # 发起GET请求，获取当前某分馆各区域剩余的座位数，成功则返回json，否则返回False
    def GetRooms(self, buildingId):
        url = self.stats_url + buildingId
        print('\nTry getting room information...Status: ', end='')
        try:
            response = requests.get(url, headers=self.headers, verify=False)
            json = response.json()
            print(str(json['status']))
            if json['status'] == 'success':
                print('\n当前座位状态：')
                for room in json['data']:
                    print('\n' + room['room'] + '\n楼层：' + str(room['floor']) + '\n总座位数：' +
                          str(room['totalSeats']) + '\n已预约：' + str(room['reserved']) +
                          '\n正在使用：' + str(room['inUse']).ljust(3) + '\n暂离：' +
                          str(room['away']) + '\n空闲：' + str(room['free']))
                return True
            else:
                print(json)
                return False
        except:
            print('Connection lost')
            return False

    # 发起GET请求，获取当前的座位预约记录，若已有有效预约则返回预约id，否则返回False
    def CheckResInf(self):
        url = self.history_url + '30'
        print('\nTry getting reservation information...Status: ', end='')
        try:
            response = requests.get(url, headers=self.headers, verify=False)
            json = response.json()
            print(str(json['status']))
            if json['status'] == 'success':
                for reservation in json['data']['reservations']:
                    if reservation['stat'] in ['RESERVE', 'CHECK_IN', 'AWAY']:
                        print('\n--------------------已检测到有效预约---------------------')
                        print('ID：' + str(reservation['id']))
                        print('时间：' + reservation['date'] + ' ' + reservation['begin'] + '～' + reservation['end'])
                        if reservation['awayBegin'] and reservation['awayEnd']:
                            print('暂离时间：' + reservation['awayBegin'] + '～' + reservation['awayEnd'])
                        elif reservation['awayBegin'] and not reservation['awayEnd']:
                            print('暂离时间：' + reservation['awayBegin'])
                        print('状态：' + self.state.get(reservation['stat']))
                        print('地址：' + reservation['loc'])
                        print('------------------------------------------------------')

                        if '3C创客空间' in reservation['loc'] and reservation['stat'] == 'RESERVE':
                            if input('\n该座位位于\'一楼3C创客空间\'，是否进入换座模式（1.是 2.否）：') == '1':
                                self.ExchangeLoop(
                                    str(int(reservation['begin'][:2]) * 60 + int(reservation['begin'][-2:])),
                                    str(int(reservation['end'][:2]) * 60 + int(reservation['end'][-2:])),
                                    str(reservation['id']))
                                sys.exit()

                        return (str(reservation['id']) if reservation['stat'] == 'RESERVE' else 'using')
                print('\n未检测到有效预约')
                return False
            else:
                print('\n检测有效预约失败')
                return False
        except:
            print('Connection lost')
            return False

    # 发起GET请求，获取当前某区域内的位置信息，成功则返回json，否则返回False
    def GetSeats(self, roomId, date):
        url = self.layout_url + roomId + '/' + date
        print('\nTry getting seat information...Status: ', end='')
        try:
            response = requests.get(url, headers=self.headers, verify=False)
            json = response.json()
            print(str(json['status']))
            if json['status'] == 'success':
                self.allSeats = {}
                for seat in json['data']['layout']:
                    if json['data']['layout'][seat]['type'] == 'seat':
                        self.allSeats[json['data']['layout'][seat]['name']] = str(json['data']['layout'][seat]['id'])
                return True
            else:
                print(json)
                return False
        except:
            print('Connection lost')
            return False

    # 发起GET请求，检索某区域内指定时间段的空位，成功则返回'Success'并将seatId存入freeSeats数组中，否则返回'Failed'，连接丢失则返回'Connection lost'
    def SearchFreeSeat(self, buildingId, roomId, date, startTime, endTime, batch='9999', page='1'):
        url = self.search_url + date + '/' + startTime + '/' + endTime
        datas = {'t': '1', 'roomId': roomId, 'buildingId': buildingId, 'batch': batch, 'page': page, 't2': '2'}
        print('\nTry searching for free seats in room ' + roomId + '...Status:', end='')
        try:
            response = requests.post(url, headers=self.headers, data=datas, verify=False)
            json = response.json()
            if json['data']['seats'] != {}:
                print('success')
                for num in json['data']['seats']:
                    self.freeSeats.append(json['data']['seats'][num]['id'])
                return 'Success'
            else:
                print('failed')
                return 'Failed'
        except:
            print('Connection lost')
            return 'Connection lost'

    # 发起POST请求，尝试预定指定座位，成功则打印预定信息并返回'Success'，失败则返回'Failed'，连接丢失则返回'Connection lost'
    def BookSeat(self, seatId, date, startTime, endTime):
        datas = {'t': '1', 'startTime': startTime, 'endTime': endTime, 'seat': seatId, 'date': date, 't2': '2'}
        print('\nTry booking seat...Status: ', end='')
        try:
            response = requests.post(self.book_url, headers=self.headers, data=datas, verify=False)
            json = response.json()
            print(str(json['status']))
            if json['status'] == 'success':
                self.PrintBookInf(json)
                if self.to_addr:
                    if self.SendMail(json):
                        print('\n邮件提醒发送成功，若接收不到提醒，请将\'seatkiller@outlook.com\'添加至邮箱白名单')
                    else:
                        print('\n邮件提醒发送失败')
                if '3C创客空间' in json['data']['location']:
                    return str(json['data']['id'])
                else:
                    return 'Success'
            else:
                print(json)
                return 'Failed'
        except:
            print('Connection lost')
            return 'Connection lost'

    # 发起GET请求，取消指定id的座位预约，成功则返回True，否则返回False
    def CancelReservation(self, id):
        url = self.cancel_url + id
        print('\nTry cancelling reservation...Status: ', end='')
        try:
            response = requests.get(url, headers=self.headers, verify=False)
            json = response.json()
            print(str(json['status']))
            if json['status'] == 'success':
                return True
            else:
                print(json)
                return False
        except:
            print('Connection lost')
            return False

    # 发起GET请求，释放当前正在使用的座位，成功则返回True，否则返回False
    def StopUsing(self):
        print('\nTry releasing seat...Status: ', end='')
        try:
            response = requests.get(self.stop_url, headers=self.headers, verify=False)
            json = response.json()
            print(str(json['status']))
            if json['status'] == 'success':
                return True
            else:
                print(json)
                return False
        except:
            print('Connection lost')
            return False

    # 打印座位预约凭证
    def PrintBookInf(self, json):
        print('\n--------------------座位预约成功!--------------------')
        print('ID：' + str(json['data']['id']))
        print('凭证号码：' + json['data']['receipt'])
        print('时间：' + json['data']['onDate'] + ' ' + json['data']['begin'] + '～' + json['data']['end'])
        print('状态：' + ('已签到' if json['data']['checkedIn'] else '预约'))
        print('地址：' + json['data']['location'])
        print('---------------------------------------------------')

    # 建立Socket套接字连接，将预约信息发送到邮件服务器
    def SendMail(self, json):
        print('\n尝试连接邮件发送服务器...')
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(15)
            s.connect(('120.79.81.183', 5210))

            if s.recv(1024).decode('utf-8') == 'Hello':
                print('连接成功')

            s.send(bytes('json' + str(json), 'utf-8'))
            print(s.recv(1024).decode('utf-8'))

            s.send(bytes(self.to_addr, 'utf-8'))
            print(s.recv(1024).decode('utf-8'))

            print('正在尝试发送邮件提醒至\'' + self.to_addr + '\'...')
            s.send(b'SendMail')
            if s.recv(1024).decode('utf-8') == 'success':
                s.send(b'exit')
                s.close()
                return True
            else:
                s.send(b'exit')
                s.close()
                return False
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
                        print('\n连接丢失，30秒后尝试继续检索空位')
                        time.sleep(30)
                for freeSeatId in self.freeSeats:
                    response = self.BookSeat(freeSeatId, date, startTime, endTime)
                    if response[0] in map(str, range(10)) or response == 'Success':
                        print('\n捡漏成功')
                        print('\n-------------------------捡漏模式结束--------------------------')
                        return response
                    elif response == 'Failed':
                        time.sleep(random.uniform(1, 3))
                        continue
                    else:
                        print('\n连接丢失，1分钟后尝试继续抢座')
                        time.sleep(60)
                        continue
                else:
                    ddl = datetime.datetime.replace(datetime.datetime.now(), hour=20, minute=0, second=0)
                    delta = ddl - datetime.datetime.now()
                    print('\n循环结束，3秒后进入下一个循环，运行时间剩余' + str(delta.seconds) + '秒\n')
                    time.sleep(3)
            else:
                print('\n获取token失败，1分钟后再次尝试')
                time.sleep(60)

            if datetime.datetime.now() >= datetime.datetime.replace(datetime.datetime.now(), hour=20,
                                                                    minute=0, second=0):
                print('\n捡漏失败，超出运行时间')
                print('\n-------------------------捡漏模式结束--------------------------')
                return False

    # 换座模式（限信息科学分馆）
    def ExchangeLoop(self, startTime, endTime, id, nextDay=False):
        print('\n-------------------------换座模式开始--------------------------')
        if nextDay:
            date = datetime.date.today() + datetime.timedelta(days=1)
        else:
            date = datetime.date.today()
        date = date.strftime('%Y-%m-%d')
        cancel = False
        cancelled = False
        while True:
            self.freeSeats = []
            if self.GetToken():
                for i in self.xt_less:
                    res = self.SearchFreeSeat('1', i, date, startTime, endTime)
                    if res == 'Success' and not cancelled:
                        cancel = True
                    elif res == 'Connection lost':
                        print('\n连接丢失，30秒后尝试继续检索空位')
                        time.sleep(30)
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
                        time.sleep(random.uniform(1, 3))
                        continue
                    else:
                        print('\n连接丢失，1分钟后尝试继续抢座')
                        time.sleep(60)
                        continue
                else:
                    ddl = datetime.datetime.replace(datetime.datetime.now(), hour=20, minute=0, second=0)
                    delta = ddl - datetime.datetime.now()
                    print('\n循环结束，3秒后进入下一个循环，运行时间剩余' + str(delta.seconds) + '秒\n')
                    time.sleep(3)
            else:
                print('\n获取token失败，1分钟后再次尝试')
                time.sleep(60)

            if datetime.datetime.now() >= datetime.datetime.replace(datetime.datetime.now(), hour=20,
                                                                    minute=0, second=0):
                if cancelled:
                    print('\n换座失败，原座位已丢失')
                else:
                    print('\n换座失败，原座位未丢失')
                print('\n-------------------------换座模式结束--------------------------')
                return False
