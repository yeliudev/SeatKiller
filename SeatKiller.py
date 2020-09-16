# Copyright (c) Ye Liu. All rights reserved.

import datetime
import json
import random
import socket
import sys
import time

import requests

API_ROOT = 'https://seat.lib.whu.edu.cn:8443/rest/'

LOGIN_URL = API_ROOT + 'auth'
USER_URL = API_ROOT + 'v2/user'
FILTERS_URL = API_ROOT + 'v2/free/filters'
STATS_URL = API_ROOT + 'v2/room/stats2/'
LAYOUT_URL = API_ROOT + 'v2/room/layoutByDate/'
SEARCH_URL = API_ROOT + 'v2/searchSeats/'
STARTTIME_URL = API_ROOT + 'v2/startTimesForSeat/'
ENDTIME_URL = API_ROOT + 'v2/endTimesForSeat/'
HISTORY_URL = API_ROOT + 'v2/history/1/'
BOOK_URL = API_ROOT + 'v2/freeBook'
CANCEL_URL = API_ROOT + 'v2/cancel/'
STOP_URL = API_ROOT + 'v2/stop'


class SeatKiller(object):

    def __init__(self, username='', password=''):
        self.allSeats = {}
        self.freeSeats = []
        self.startTimes = []
        self.endTimes = []
        self.token = ''
        self.username = username
        self.password = password
        self.to_addr = ''
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'doSingle/11 CFNetwork/893.14.2 Darwin/17.3.0',
            'token': self.token
        }
        self.state = {'RESERVE': '预约', 'CHECK_IN': '履约中', 'AWAY': '暂离'}

    def wait(self, hour, minute, second, nextDay=False):
        if nextDay:
            time_run = datetime.datetime.replace(
                datetime.datetime.now() + datetime.timedelta(days=1),
                hour=hour,
                minute=minute,
                second=second)
        else:
            time_run = datetime.datetime.replace(
                datetime.datetime.now(),
                hour=hour,
                minute=minute,
                second=second)
        print('\n', end='')
        while True:
            delta = time_run - datetime.datetime.now()
            if delta.total_seconds() <= 0:
                print('\n', end='')
                break
            print(
                '\r正在等待系统开放...剩余' + str(int(delta.total_seconds())) + '秒',
                end='    ')
            time.sleep(0.05)

    def get_token(self):
        datas = {'username': self.username, 'password': self.password}
        print('\nTry getting token...Status: ', end='')
        try:
            response = requests.get(
                LOGIN_URL,
                params=datas,
                headers=self.headers,
                verify=False,
                timeout=5)
            json = response.json()
            print(json['status'])
            if json['status'] == 'success':
                self.token = json['data']['token']
                self.headers['token'] = self.token
                print('token：' + json['data']['token'])
                return json['data']['token']
            else:
                print(json['message'])
                return False
        except Exception:
            print('Connection lost')
            return False

    def get_user_info(self):
        try:
            response = requests.get(
                USER_URL, headers=self.headers, verify=False, timeout=5)
            json = response.json()
            if json['status'] == 'success':
                self.name = json['data']['name']
                print('\n你好，' + self.name + ' 上次入馆时间：' + json['data']
                      ['lastLogin'].replace('T', ' ').rstrip('.000') + ' 状态：' +
                      ('已进入' + json['data']['lastInBuildingName'] + ' 入馆时间：' +
                       json['data']['lastIn']
                       if json['data']['checkedIn'] else '未入馆') + ' 违约记录：' +
                      str(json['data']['violationCount']) + '次')
                return True
            else:
                print('\nTry getting user information...Status: failed')
                return False
        except Exception:
            print('\nTry getting user information...Status: Connection lost')
            return False

    def get_buildings(self):
        print('\nTry getting building information...Status: ', end='')
        try:
            response = requests.get(
                FILTERS_URL, headers=self.headers, verify=False, timeout=5)
            json = response.json()
            print(json['status'])
            if json['status'] == 'success':
                return json
            else:
                print(json)
                return False
        except Exception:
            print('Connection lost')
            return False

    def get_rooms(self, buildingId):
        url = STATS_URL + buildingId
        print('\nTry getting room information...Status: ', end='')
        try:
            response = requests.get(
                url, headers=self.headers, verify=False, timeout=5)
            json = response.json()
            print(json['status'])
            if json['status'] == 'success':
                print('\n当前座位状态：')
                for room in json['data']:
                    print('\n' + room['room'] + '\n楼层：' + str(room['floor']) +
                          '\n总座位数：' + str(room['totalSeats']) + '\n已预约：' +
                          str(room['reserved']) + '\n正在使用：' +
                          str(room['inUse']).ljust(3) + '\n暂离：' +
                          str(room['away']) + '\n空闲：' + str(room['free']))
                return True
            else:
                print(json)
                return False
        except Exception:
            print('Connection lost')
            return False

    def check_res_info(self):
        url = HISTORY_URL + '30'
        print('\nTry getting reservation information...Status: ', end='')
        try:
            response = requests.get(
                url, headers=self.headers, verify=False, timeout=5)
            json = response.json()
            print(json['status'])
            if json['status'] == 'success':
                for reservation in json['data']['reservations']:
                    if reservation['stat'] in ['RESERVE', 'CHECK_IN', 'AWAY']:
                        print(
                            '\n--------------------已检测到有效预约---------------------'  # noqa
                        )
                        print('ID：' + str(reservation['id']))
                        print('时间：' + reservation['date'] + ' ' +
                              reservation['begin'] + '～' + reservation['end'])
                        if reservation['awayBegin'] and reservation['awayEnd']:
                            print('暂离时间：' + reservation['awayBegin'] + '～' +
                                  reservation['awayEnd'])
                        elif reservation[
                                'awayBegin'] and not reservation['awayEnd']:
                            print('暂离时间：' + reservation['awayBegin'])
                        print('状态：' + self.state.get(reservation['stat']))
                        print('地址：' + reservation['loc'])
                        print(
                            '------------------------------------------------------'  # noqa
                        )

                        if '3C创客空间' in reservation['loc'] and reservation[
                                'stat'] == 'RESERVE':
                            if input('\n该座位位于\'一楼3C创客空间\'，是否进入改签模式（1.是 2.否）：'
                                     ) == '1':
                                self.exchange_loop(
                                    '1', XT_LITE,
                                    str(
                                        int(reservation['begin'][:2]) * 60 +
                                        int(reservation['begin'][-2:])),
                                    str(
                                        int(reservation['end'][:2]) * 60 +
                                        int(reservation['end'][-2:])),
                                    str(reservation['id']))
                                sys.exit()

                        return str(
                            reservation['id']
                        ) if reservation['stat'] == 'RESERVE' else 'using'
                print('\n未检测到有效预约')
                return False
            else:
                print('\n检测有效预约失败')
                return False
        except Exception:
            print('Connection lost')
            return False

    def get_seats(self, roomId, date):
        url = LAYOUT_URL + roomId + '/' + date
        print('\nTry getting seat information...Status: ', end='')
        try:
            response = requests.get(
                url, headers=self.headers, verify=False, timeout=5)
            json = response.json()
            print(json['status'])
            if json['status'] == 'success':
                self.allSeats = {}
                for seat in json['data']['layout']:
                    if json['data']['layout'][seat]['type'] == 'seat':
                        self.allSeats[json['data']['layout'][seat]
                                      ['name']] = str(
                                          json['data']['layout'][seat]['id'])
                return True
            else:
                print(json)
                return False
        except Exception:
            print('Connection lost')
            return False

    def search_free_seat(self,
                         buildingId,
                         roomId,
                         date,
                         startTime,
                         endTime,
                         batch='9999',
                         page='1'):
        url = SEARCH_URL + date + '/' + startTime + '/' + endTime
        datas = {
            't': '1',
            'roomId': roomId,
            'buildingId': buildingId,
            'batch': batch,
            'page': page,
            't2': '2'
        }
        print(
            '\nTry searching for free seats in room ' + roomId + '...Status: ',
            end='')
        try:
            response = requests.post(
                url, headers=self.headers, data=datas, verify=False, timeout=5)
            json = response.json()
            if json['data']['seats'] != {}:
                print('success')
                for num in json['data']['seats']:
                    self.freeSeats.append(
                        str(json['data']['seats'][num]['id']))
                return 'Success'
            else:
                print('failed')
                return 'Failed'
        except Exception:
            print('Connection lost')
            return 'Connection lost'

    def check_start_time(self, seatId, date, startTime):
        url = STARTTIME_URL + seatId + '/' + date
        print(
            '\nTry checking startTimes of seat No.' + seatId + '...Status: ',
            end='')
        try:
            response = requests.get(
                url, headers=self.headers, verify=False, timeout=5)
            json = response.json()
            if json['status'] == 'success':
                self.startTimes.clear()
                for startTimeJson in json['data']['startTimes']:
                    self.startTimes.append(startTimeJson['id'])
                if startTime in self.startTimes:
                    print('success')
                    return True
                else:
                    print('fail')
                    return False
            else:
                print('fail')
                return False
        except Exception:
            print('Connection lost')
            return False

    def check_end_time(self, seatId, date, startTime, endTime):
        url = ENDTIME_URL + seatId + '/' + date + '/' + startTime
        print(
            '\nTry checking endTimes of seat No.' + seatId + '...Status: ',
            end='')
        try:
            response = requests.get(
                url, headers=self.headers, verify=False, timeout=5)
            json = response.json()
            if json['status'] == 'success':
                self.endTimes.clear()
                for endTimeJson in json['data']['endTimes']:
                    self.endTimes.append(endTimeJson['id'])
                if endTime in self.endTimes:
                    print('success')
                    return True
                else:
                    print('fail')
                    return False
            else:
                print('fail')
                return False
        except Exception:
            print('Connection lost')
            return False

    def book_seat(self, seatId, date, startTime, endTime):
        datas = {
            't': '1',
            'startTime': startTime,
            'endTime': endTime,
            'seat': seatId,
            'date': date,
            't2': '2'
        }
        print('\nTry booking seat...Status: ', end='')
        try:
            response = requests.post(
                BOOK_URL,
                headers=self.headers,
                data=datas,
                verify=False,
                timeout=5)
            json = response.json()
            print(json['status'])
            if json['status'] == 'success':
                self.print_book_info(json)
                if self.to_addr:
                    self.send_mail(json)
                if '3C创客空间' in json['data']['location']:
                    return str(json['data']['id'])
                else:
                    return 'Success'
            else:
                print(json)
                return 'Failed'
        except Exception:
            print('Connection lost')
            return 'Connection lost'

    def cancel_res(self, id):
        url = CANCEL_URL + id
        print('\nTry cancelling reservation...Status: ', end='')
        try:
            response = requests.get(
                url, headers=self.headers, verify=False, timeout=5)
            json = response.json()
            print(json['status'])
            if json['status'] == 'success':
                return True
            else:
                print(json)
                return False
        except Exception:
            print('Connection lost')
            return False

    def stop_using(self):
        print('\nTry releasing seat...Status: ', end='')
        try:
            response = requests.get(
                STOP_URL, headers=self.headers, verify=False, timeout=5)
            json = response.json()
            print(json['status'])
            if json['status'] == 'success':
                return True
            else:
                print(json)
                return False
        except Exception:
            print('Connection lost')
            return False

    def print_book_info(self, json):
        print('\n--------------------座位预约成功!--------------------')
        print('ID：' + str(json['data']['id']))
        print('凭证号码：' + json['data']['receipt'])
        print('时间：' + json['data']['onDate'] + ' ' + json['data']['begin'] +
              '～' + json['data']['end'])
        print('状态：' + ('已签到' if json['data']['checkedIn'] else '预约'))
        print('地址：' + json['data']['location'])
        print('---------------------------------------------------')

    def send_mail(self, jsonCode):
        jsonCode['username'] = self.username
        jsonCode['name'] = self.name
        jsonCode['client'] = 'Python'
        print('\n正在尝试发送邮件提醒至\'' + self.to_addr + '\'...')
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect(('134.175.186.17', 5210))

            if s.recv(5).decode() == 'hello':
                s.send(
                    bytes(
                        'json ' + str(
                            json.dumps(jsonCode, ensure_ascii=False,
                                       indent=2)), 'utf-8'))

                if s.recv(7).decode() == 'success':
                    print(
                        '邮件提醒发送成功，若接收不到提醒，请将\'seatkiller@outlook.com\'添加至邮箱白名单'
                    )
                else:
                    print('邮件提醒发送失败')

            s.close()
        except Exception:
            return

    def loop(self, buildingId, rooms, startTime, endTime):
        print('\n-------------------------捡漏模式开始--------------------------')
        date = datetime.date.today()
        date = date.strftime('%Y-%m-%d')
        while True:
            self.freeSeats = []
            if self.get_token():
                for i in rooms:
                    if self.search_free_seat(buildingId, i, date, startTime,
                                             endTime) == 'Connection lost':
                        print('\n连接丢失，30秒后尝试继续检索空位')
                        time.sleep(30)
                for freeSeatId in self.freeSeats:
                    response = self.book_seat(freeSeatId, date, startTime,
                                              endTime)
                    if response[0] in map(str,
                                          range(10)) or response == 'Success':
                        print('\n捡漏成功')
                        print(
                            '\n-------------------------捡漏模式结束--------------------------'  # noqa
                        )
                        return response
                    elif response == 'Failed':
                        time.sleep(random.uniform(1, 3))
                        continue
                    else:
                        print('\n连接丢失，1分钟后尝试继续抢座')
                        time.sleep(60)
                        continue
                else:
                    ddl = datetime.datetime.replace(
                        datetime.datetime.now(), hour=20, minute=0, second=0)
                    delta = ddl - datetime.datetime.now()
                    print('\n循环结束，3秒后进入下一个循环，运行时间剩余' + str(delta.seconds) +
                          '秒\n')
                    time.sleep(3)
            else:
                print('\n获取token失败，1分钟后再次尝试')
                time.sleep(60)

            if datetime.datetime.now() >= datetime.datetime.replace(
                    datetime.datetime.now(), hour=20, minute=0, second=0):
                print('\n捡漏失败，超出运行时间')
                print(
                    '\n-------------------------捡漏模式结束--------------------------'  # noqa
                )
                return False

    def exchange_loop(self,
                      buildingId,
                      rooms,
                      startTime,
                      endTime,
                      id,
                      nextDay=False):
        print('\n-------------------------改签模式开始--------------------------')
        if nextDay:
            date = datetime.date.today() + datetime.timedelta(days=1)
        else:
            date = datetime.date.today()
        date = date.strftime('%Y-%m-%d')
        cancelled = False
        while True:
            self.freeSeats = []
            if self.get_token():
                for i in rooms:
                    res = self.search_free_seat(buildingId, i, date, startTime,
                                                endTime)
                    if res == 'Connection lost':
                        print('\n连接丢失，30秒后尝试继续检索空位')
                        time.sleep(30)
                for freeSeatId in self.freeSeats:
                    if not self.check_start_time(freeSeatId, date, startTime):
                        continue
                    if not self.check_end_time(freeSeatId, date, startTime,
                                               endTime):
                        continue
                    if self.cancel_res(id):
                        cancelled = True
                    response = self.book_seat(freeSeatId, date, startTime,
                                              endTime)
                    if response == 'Success':
                        print('\n改签成功')
                        print(
                            '\n-------------------------改签模式结束--------------------------'  # noqa
                        )
                        return True
                    elif response == 'Failed':
                        time.sleep(random.uniform(1, 3))
                        continue
                    else:
                        print('\n连接丢失，1分钟后尝试继续抢座')
                        time.sleep(60)
                        continue
                else:
                    ddl = datetime.datetime.replace(
                        datetime.datetime.now(), hour=20, minute=0, second=0)
                    delta = ddl - datetime.datetime.now()
                    print('\n循环结束，3秒后进入下一个循环，运行时间剩余' + str(delta.seconds) +
                          '秒\n')
                    time.sleep(3)
            else:
                print('\n获取token失败，1分钟后再次尝试')
                time.sleep(60)

            if datetime.datetime.now() >= datetime.datetime.replace(
                    datetime.datetime.now(), hour=20, minute=0, second=0):
                if cancelled:
                    print('\n改签失败，原座位已丢失')
                else:
                    print('\n改签失败，原座位未丢失')
                print(
                    '\n-------------------------改签模式结束--------------------------'  # noqa
                )
                return False
