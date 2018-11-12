# SeatKiller

[![Build Status](https://img.shields.io/travis/goolhanrry/SeatKiller.svg?branch=master)](https://www.travis-ci.org/goolhanrry/SeatKiller)
[![License](https://img.shields.io/badge/license-MPL--2.0-red.svg)](LICENSE)
[![Language](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/)
[![GitHub repo size in bytes](https://img.shields.io/github/repo-size/goolhanrry/SeatKiller.svg?colorB=ff7e00#)](https://github.com/goolhanrry/SeatKiller)

偶然发现图书馆的服务器没设防，于是写了这个小工具练练手，欢迎添加我的微信：`aweawds` 交流讨论

该仓库已停止维护，所有功能已经移植到了用 C# 重写的 GUI 版本：[SeatKiller_UI](https://github.com/goolhanrry/SeatKiller_UI)

## 已经实现的功能

* 获取用户的信息，包括姓名、当前状态（未入馆、已进入某分馆）和累计违约次数
* 晚上 22:15 定时抢座（可自行选择是否指定区域、座位号）
* 检测是否已有有效预约，区分状态（预约、履约中、暂离），并可取消或释放座位
* 预约成功后连接邮件服务器发送邮件提醒
* 捡漏模式可用于抢当天座位
* 改签模式可用于在已有有效预约的情况下，更换座位或改签预约时间（如果空闲），确保新座位可用的情况下再释放原座位，防止座位丢失

## 即将实现的功能

* 暂无

## 使用方法

1. 配置 [Python3](https://www.python.org/) 运行环境 (已经配置好环境的可忽略此步骤)
2. Terminal 或 CMD 执行 `pip3 install requests` 安装 requests 库
3. 运行 `main.py` ，按提示输入相关参数，即可实现自动抢座

## 软件截图

<p align="center">
  <img with="999" height="666" src="https://github.com/goolhanrry/SeatKiller/blob/master/Screenshot/SeatKiller_Screenshot.png" alt="screenshot">
</p>
