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

xt = ['6', '7', '8', '9', '10', '11', '12']
gt = ['19', '29', '31', '32', '33', '34', '35', '37', '38']
yt = ['20', '21', '23', '24', '26', '27']
zt = ['39', '40', '51', '52', '56', '59', '60', '61', '62', '65', '66']


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
    rooms = xt
else:
    buildingId = input('请输入图书馆编号（1.信息科学分馆 2.工学分馆 3.医学分馆 4.总馆）：')
    if buildingId == '1':
        rooms = xt
        roomId = input('已获取区域列表：4.一楼3C创客空间\n             5.一楼创新学习讨论区\n             6.二楼西自然科学图书借阅区\n'
                       '             7.二楼东自然科学图书借阅区\n             8.三楼西社会科学图书借阅区\n             9.四楼西图书阅览区\n'
                       '             10.三楼东社会科学图书借阅区\n             11.四楼东图书阅览区\n             12.三楼自主学习区\n'
                       '             14.3C创客-双屏电脑（20台）\n             15.创新学习-MAC电脑（12台）\n'
                       '             16.创新学习-云桌面（42台）\n请输入房间编号（若由系统自动选择请输入1）：')
    elif buildingId == '2':
        rooms = gt
        roomId = input('已获取区域列表：19.201室-东部自科图书借阅区\n             29.2楼-中部走廊\n             31.205室-中部电子阅览室笔记本区\n'
                       '             32.301室-东部自科图书借阅区\n             33.305室-中部自科图书借阅区\n             34.401室-东部自科图书借阅区\n'
                       '             35.405室中部期刊阅览区\n             37.501室-东部外文图书借阅区\n             38.505室-中部自科图书借阅区\n'
                       '请输入区域编号（若由系统自动选择请输入1）：')
    elif buildingId == '3':
        rooms = yt
        roomId = input('已获取区域列表：20.204教学参考书借阅区\n             21.302中文科技图书借阅B区\n             23.305科技期刊阅览区\n'
                       '             24.402中文文科图书借阅区\n             26.502外文图书借阅区\n             27.506医学人文阅览区\n'
                       '请输入房间编号（若由系统自动选择请输入1）：')
    else:
        rooms = zt
        roomId = input('已获取区域列表：39.A1-座位区\n             40.C1自习区\n             51.A2\n             52.A3\n'
                       '             56.B3\n             59.B2\n             60.A4\n             61.A5\n'
                       '             62.A1-沙发区\n             65.B1\n             66.A1-苹果区\n'
                       '请输入房间编号（若由系统自动选择请输入1）：')

    if roomId != '1':
        seatID = input('请输入座位ID（若由系统自动选择请输入1）：')
    else:
        seatID = '1'

    startTime = input('请输入开始时间（以分钟为单位，从0点开始计算）：')
    endTime = input('请输入结束时间（以分钟为单位，从0点开始计算）：')

while True:
    wait(22, 14, 30)
    try_booking = True
    date = datetime.date.today()
    date = date.strftime('%Y-%m-%d')
    print('\ndate:' + date)

    stats_url = stats_url + buildingId
    layout_url = layout_url + roomId + '/' + date
    search_url = search_url + date + '/' + startTime + '/' + endTime

    token = GetToken(login_url, token, username, password)
    if token != 'failed':
        GetBuildings(filters_url, token)
        GetRooms(stats_url, token)
        if roomId != '1':
            GetSeats(layout_url, token)

        wait(22, 15, 0)
        if seatID == '1':
            while (try_booking == True):
                if BookSeat(book_url, token, startTime, endTime, 7469, date) == 'success':
                    try_booking = False
                    break
                elif datetime.datetime.now() >= datetime.datetime.replace(datetime.datetime.now(), hour=23, minute=45,
                                                                          second=0):
                    print('\n抢座失败，座位预约系统已关闭，2小时后尝试重新抢座')
                    time.sleep(7200)
                    freeSeats = []
                    date = datetime.date.today()
                    date = date.strftime('%Y-%m-%d')
                    token = GetToken(login_url, token, username, password)
                    if token != 'failed':
                        SearchFreeSeat(search_url, token, 4, 1)
                        for freeSeatId in freeSeats:
                            response = BookSeat(book_url, token, startTime, endTime, freeSeatId, date)
                            if response == 'success':
                                try_booking = False
                                break
                            elif response == 'failed':
                                time.sleep(5)
                                continue
                            else:
                                if freeSeatId != freeSeats(-1):
                                    print('\n连接丢失，2分钟后尝试继续抢座')
                                    time.sleep(120)
                                    continue
                                break
                    print('\n抢座运行结束')
                    try_booking = False
                    break
                else:
                    freeSeats = []
                    if roomId == '1' and seatID == '1':
                        for i in rooms:
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
                            ddl = datetime.datetime.replace(datetime.datetime.now(), hour=23, minute=45, second=0)
                            delta = ddl - datetime.datetime.now()
                            print('\n连接丢失，30秒后尝试重新抢座，系统开放时间剩余' + str(delta.seconds) + '秒\n')
                            time.sleep(30)
                            break
        else:
            for i in range(1, 50):
                if BookSeat(book_url, token, startTime, endTime, seatID, date) == 'success' or 'failed':
                    break
        time.sleep(14400)
