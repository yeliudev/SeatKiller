#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import datetime
import time

login_url = 'https://seat.lib.whu.edu.cn:8443/rest/auth'
filters_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/free/filters'
stats_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/room/stats2/'
layout_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/room/layoutByDate/'
book_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/freeBook'
token = '75PLJJO8PV12084027'


def wait(hour, minute, second):
    time_run = datetime.datetime.replace(datetime.datetime.now(), hour=hour, minute=minute, second=second)
    delta = time_run - datetime.datetime.now()
    print('\n正在等待系统开放...剩余' + str(delta.seconds) + '秒')
    time.sleep(delta.seconds)


def GetToken(url, token):
    headers = {'Host': 'seat.lib.whu.edu.cn:8443', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
               'Connection': 'keep-alive', 'Accept': '*/*',
               'User-Agent': 'doSingle/11 CFNetwork/893.14.2 Darwin/17.3.0',
               'Accept-Language': 'zh-cn', 'token': token, 'Accept-Encoding': 'gzip, deflate'}
    datas = {'username': '2016301130016', 'password': '194614'}
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
    json = response.json()
    print('\nTry getting building information...Status: ' + str(json['status']))
    if json['status'] == 'success':
        return json
    else:
        print(json)
        return 'failed'


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


if input('请输入抢座模式（1.自动 2.手动）：') == '1':
    building_num = '1'
    room_num = '9'
    book_date = '2'
    seatID = '7469'
    startTime = '480'
    endTime = '1410'
else:
    building_num = input('请输入图书馆编号（1.信息科学分馆 2.工学分馆 3.医学分馆 4.总馆）：')
    if building_num == '1':
        room_num = input('已获取房间列表：4.一楼3C创客空间\n             5.一楼创新学习讨论区\n             6.二楼西自然科学图书借阅区\n'
                         '             7.二楼东自然科学图书借阅区\n             8.三楼西社会科学图书借阅区\n             9.四楼西图书阅览区\n'
                         '             10.三楼东社会科学图书借阅区\n             11.四楼东图书阅览区\n             12.三楼自主学习区\n'
                         '             14.3C创客-双屏电脑（20台）\n             15.创新学习-MAC电脑（12台）\n'
                         '             16.创新学习-云桌面（42台）\n请输入房间编号：')
    book_date = input('请输入预约日期（1.当日 2.次日）：')
    seatID = input('请输入座位ID：')
    startTime = input('请输入开始时间（以分钟为单位）：')
    endTime = input('请输入结束时间（以分钟为单位）：')

while True:
    date = datetime.date.today()
    if book_date == '1':
        date = date.strftime('%Y-%m-%d')
    else:
        date = date + datetime.timedelta(days=1)
        date = date.strftime('%Y-%m-%d')

    stats_url = stats_url + building_num
    layout_url = layout_url + room_num + '/' + date

    wait(22, 29, 0)
    token = GetToken(login_url, token)
    if token != 'fail':
        GetBuildings(filters_url, token)
        GetRooms(stats_url, token)
        GetSeats(layout_url, token)

        wait(22, 30, 0)
        for i in range(1, 100):
            if BookSeat(book_url, token, startTime, endTime, seatID, date) == 'success' or 'fail':
                break
        time.sleep(14400)
