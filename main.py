#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import warnings
import getpass
import datetime
import time

warnings.filterwarnings('ignore')
login_url = 'https://seat.lib.whu.edu.cn:8443/rest/auth'
filters_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/free/filters'
stats_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/room/stats2/'
layout_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/room/layoutByDate/'
search_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/searchSeats/'
book_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/freeBook'
token = '75PLJJO8PV12084027'


def wait(hour, minute, second):
    time_run = datetime.datetime.replace(datetime.datetime.now(), hour=hour, minute=minute, second=second)
    delta = time_run - datetime.datetime.now()
    print('\n正在等待系统开放...剩余' + str(delta.seconds) + '秒')
    time.sleep(delta.seconds)


def GetToken(url, token, username, password):
    headers = {'Host': 'seat.lib.whu.edu.cn:8443', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
               'Connection': 'keep-alive', 'Accept': '*/*',
               'User-Agent': 'doSingle/11 CFNetwork/893.14.2 Darwin/17.3.0',
               'Accept-Language': 'zh-cn', 'token': token, 'Accept-Encoding': 'gzip, deflate'}
    datas = {'username': username, 'password': password}
    response = requests.get(url, params=datas, headers=headers, verify=False)
    try:
        json = response.json()
        print('\nTry getting token...Status: ' + str(json['status']))
        if json['status'] == 'success':
            print('token：' + json['data']['token'])
            return json['data']['token']
        else:
            print(json)
            return 'failed'
    except:
        print('\nTry getting token...Status: Connection lost')


def GetBuildings(url, token):
    headers = {'Host': 'seat.lib.whu.edu.cn:8443', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
               'Connection': 'keep-alive', 'Accept': '*/*',
               'User-Agent': 'doSingle/11 CFNetwork/893.14.2 Darwin/17.3.0',
               'Accept-Language': 'zh-cn', 'token': token, 'Accept-Encoding': 'gzip, deflate'}
    response = requests.get(url, headers=headers, verify=False)
    try:
        json = response.json()
        print('\nTry getting building information...Status: ' + str(json['status']))
        if json['status'] == 'success':
            return json
        else:
            print(json)
            return 'failed'
    except:
        print('\nTry getting building information...Status: Connection lost')
        return 'Connection lost'


def GetRooms(url, token):
    headers = {'Host': 'seat.lib.whu.edu.cn:8443', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
               'Connection': 'keep-alive', 'Accept': '*/*',
               'User-Agent': 'doSingle/11 CFNetwork/893.14.2 Darwin/17.3.0',
               'Accept-Language': 'zh-cn', 'token': token, 'Accept-Encoding': 'gzip, deflate'}
    response = requests.get(url, headers=headers, verify=False)
    try:
        json = response.json()
        print('\nTry getting room information...Status: ' + str(json['status']))
        if json['status'] == 'success':
            return json
        else:
            print(json)
            return 'failed'
    except:
        print('\nTry getting room information...Status: Connection lost')
        return 'Connection lost'


def GetSeats(url, token):
    headers = {'Host': 'seat.lib.whu.edu.cn:8443', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
               'Connection': 'keep-alive', 'Accept': '*/*',
               'User-Agent': 'doSingle/11 CFNetwork/893.14.2 Darwin/17.3.0',
               'Accept-Language': 'zh-cn', 'token': token, 'Accept-Encoding': 'gzip, deflate'}
    response = requests.get(url, headers=headers, verify=False)
    try:
        json = response.json()
        print('\nTry getting seat information...Status: ' + str(json['status']))
        if json['status'] == 'success':
            return json
        else:
            print(json)
            return 'failed'
    except:
        print('\nTry getting seat information...Status: Connection lost')
        return 'Connection lost'


def SearchFreeSeat(url, token, roomId, buildingId, batch=9999, page=1):
    headers = {'Host': 'seat.lib.whu.edu.cn:8443', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
               'Connection': 'keep-alive', 'Accept': '*/*',
               'User-Agent': 'doSingle/11 CFNetwork/893.14.2 Darwin/17.3.0',
               'Accept-Language': 'zh-cn', 'token': token, 'Accept-Encoding': 'gzip, deflate'}
    datas = {'t': '1', 'roomId': roomId, 'buildingId': buildingId, 'batch': batch, 'page': page, 't2': '2'}
    response = requests.post(url, headers=headers, data=datas, verify=False)
    try:
        json = response.json()
        if json['data']['seats'] != {}:
            print('\nTry searching for free seats in room ' + roomId + '...Status: success')
            for num in json['data']['seats']:
                freeSeats.append(json['data']['seats'][num]['id'])
            return 'success'
        else:
            print('\nTry searching for free seats in room ' + roomId + '...Status: failed')
            return 'failed'
    except:
        print('\nTry searching for free seats in room ' + roomId + '...Status: Connection lost')
        return 'Connection lost'


def BookSeat(url, token, startTime, endTime, seatID, date):
    headers = {'Host': 'seat.lib.whu.edu.cn:8443', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
               'Connection': 'keep-alive', 'Accept': '*/*',
               'User-Agent': 'doSingle/11 CFNetwork/893.14.2 Darwin/17.3.0',
               'Accept-Language': 'zh-cn', 'token': token, 'Accept-Encoding': 'gzip, deflate'}
    datas = {'t': '1', 'startTime': startTime, 'endTime': endTime, 'seat': seatID, 'date': date, 't2': '2'}
    response = requests.post(url, headers=headers, data=datas, verify=False)
    try:
        json = response.json()
        print('\nTry booking seat...Status: ' + str(json['status']))
        if json['status'] == 'success':
            print(json)
            return 'success'
        else:
            print(json)
            return 'failed'
    except:
        print('\nTry booking seat...Status: Connection lost')
        return 'Connection lost'


username = input('请输入学号：')
password = getpass.getpass('请输入图书馆密码：')

if input('请输入抢座模式（1.自动 2.手动）：') == '1':
    buildingId = '1'
    roomId = '1'
    seatID = '1'
    startTime = '480'
    endTime = '1410'
else:
    buildingId = input('请输入图书馆编号（1.信息科学分馆 2.工学分馆 3.医学分馆 4.总馆）：')
    if buildingId == '1':
        roomId = input('已获取房间列表：4.一楼3C创客空间\n             5.一楼创新学习讨论区\n             6.二楼西自然科学图书借阅区\n'
                       '             7.二楼东自然科学图书借阅区\n             8.三楼西社会科学图书借阅区\n             9.四楼西图书阅览区\n'
                       '             10.三楼东社会科学图书借阅区\n             11.四楼东图书阅览区\n             12.三楼自主学习区\n'
                       '             14.3C创客-双屏电脑（20台）\n             15.创新学习-MAC电脑（12台）\n'
                       '             16.创新学习-云桌面（42台）\n请输入房间编号（若由系统自动选择请输入1）：')
    else:
        print('暂不支持其他分馆，已自动选择信息科学分馆')
        buildingId = '1'
        roomId = input('已获取房间列表：4.一楼3C创客空间\n             5.一楼创新学习讨论区\n             6.二楼西自然科学图书借阅区\n'
                       '             7.二楼东自然科学图书借阅区\n             8.三楼西社会科学图书借阅区\n             9.四楼西图书阅览区\n'
                       '             10.三楼东社会科学图书借阅区\n             11.四楼东图书阅览区\n             12.三楼自主学习区\n'
                       '             14.3C创客-双屏电脑（20台）\n             15.创新学习-MAC电脑（12台）\n'
                       '             16.创新学习-云桌面（42台）\n请输入房间编号（若由系统自动选择请输入1）：')
    if roomId != '1':
        seatID = input('请输入座位ID（若由系统自动选择请输入1）：')
    else:
        seatID = '1'

    startTime = input('请输入开始时间（以分钟为单位）：')
    endTime = input('请输入结束时间（以分钟为单位）：')

while True:
    wait(22, 25, 0)
    try_booking = True
    date = datetime.date.today()
    print('\ndate:' + date)

    stats_url = stats_url + buildingId
    layout_url = layout_url + roomId + '/' + date
    search_url = search_url + date + '/' + startTime + '/' + endTime

    token = GetToken(login_url, token, username, password)
    if token != 'failed':
        GetBuildings(filters_url, token)
        GetRooms(stats_url, token)
        GetSeats(layout_url, token)

        wait(22, 30, 0)
        while (try_booking == True):
            freeSeats = []
            if roomId == '1' and seatID == '1':
                for i in range(6, 12):
                    SearchFreeSeat(search_url, token, i, buildingId)
            elif roomId != '1' and seatID == '1':
                SearchFreeSeat(search_url, token, roomId, buildingId)
            else:
                freeSeats.append(seatID)

            for freeSeatId in freeSeats:
                response = BookSeat(book_url, token, startTime, endTime, freeSeatId, date)
                if response == 'success':
                    try_booking = False
                    break
                elif response == 'failed':
                    continue
                else:
                    ddl = datetime.datetime.replace(datetime.datetime.now(), hour=23, minute=25, second=0)
                    delta = ddl - datetime.datetime.now()
                    print('\n连接丢失，30秒后尝试重新抢座，系统开放时间剩余' + str(delta.seconds) + '秒\n')
                    time.sleep(30)
                    if datetime.datetime.now() >= datetime.datetime.replace(datetime.datetime.now(), hour=23, minute=25,
                                                                            second=0):
                        print('\n抢座失败，座位预约系统已关闭\n')
                        try_booking = False
                        break
                    else:
                        break

        # for re_times in range(1, 100):
        #    if BookSeat(book_url, token, startTime, endTime, seatID, date) == 'success' or 'failed':
        #        break
        time.sleep(14400)
