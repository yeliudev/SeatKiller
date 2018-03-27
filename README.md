# SeatKiller

[![License](https://img.shields.io/badge/license-MIT-red.svg?colorB=D5283A#)](LICENSE)
[![Language](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/)
![GitHub last commit](https://img.shields.io/github/last-commit/goolhanrry/SeatKiller.svg)
[![GitHub repo size in bytes](https://img.shields.io/github/repo-size/goolhanrry/SeatKiller.svg?colorB=ff7e00#)](https://github.com/goolhanrry/SeatKiller)

偶然发现图书馆的服务器没设防，于是写了这个小工具练练手，随缘更新，欢迎添加我的微信：`aweawds` 交流讨论

用C#重写的GUI版本：[SeatKiller_UI](https://github.com/goolhanrry/SeatKiller_UI)

## 已经实现的功能

* 获取用户的信息，包括姓名、当前状态（未入馆、已进入某分馆）和累计违约次数
* 晚上22:15定时抢座（可自行选择是否指定区域、座位号）
* 检测是否已有有效预约，区分状态（预约、履约中、暂离），并可取消或释放座位
* 预约成功后连接邮件服务器发送邮件提醒
* 捡漏模式可用于抢当天座位

## 即将实现的功能

* 暂无

## 软件截图

<p align="center">
  <img with="999" height="666" src="https://github.com/goolhanrry/SeatKiller/blob/master/Screenshot/SeatKiller_Screenshot.png" alt="screenshot">
</p>
