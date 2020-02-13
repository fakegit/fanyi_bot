# 谷歌翻译机器人(fanyi_bot)

![GitHub top language](https://img.shields.io/github/languages/top/reycn/fanyi_bot)
[![codebeat badge](https://codebeat.co/badges/660fd5c4-7218-4408-b57a-94877e55ffdb)](https://codebeat.co/projects/github-com-reycn-fanyi_bot-master) ![version](https://img.shields.io/badge/version-2.1-red) ![License](https://img.shields.io/badge/license-MIT-000000.svg)  
为全世界语言提供中文翻译。  
[在 Telegram 上使用](https://t.me/fanyi_bot)

## 如何使用

- 私聊我，发送或转发需要翻译的文字，我会将其翻译为中文；
- 群聊中，添加我为管理员，用 "/fy" 命令回复需要翻译的消息
- [BETA] 任意聊天中 @fanyi_bot 调用翻译
- [BETA] 自动中译英。

## 功能预览

- 私聊或有管理员权限的群聊中直接翻译

  <img src="https://github.com/reycn/fanyi_bot/blob/master/src/chat.jpg?raw=true" width="300"></img>

- 在任意聊天窗口 @fanyi_bot 通过 inline query 直接查询

  <img src="https://github.com/reycn/fanyi_bot/blob/master/src/inline.jpg?raw=true" width="300"></img>

## 最近更新

- 修复了 Emoji 导致的翻译问题
- 使用配置文件的方式存储 TOKEN
- 更换了更稳定的谷歌翻译 API
- 提供了中译英的新功能。
- 新增了任意调用功能(inline mode)

## 如何部署？

- 按照 `confi.template` 文件的格式新建 `config.ini` 配置文件，将你的 [Telegram Bot Token](https://core.telegram.org/bots#6-botfather) 放入该文件中
- 安装依赖 `telepot`, `termcolor`, and `googletrans`
- 执行 `python3 main.py` / 或后台执行 `setsid python3 main.py`

## 代码依赖

- Python 3
- [telepot](https://github.com/nickoala/telepot) Python framework for Telegram Bot API
- [googletrans](https://github.com/ssut/py-googletrans) (unofficial) Googletrans: Free and Unlimited Google translate API for Python.
- [termcolor](https://github.com/hfeeki/termcolor) (fork version) fork of termcolor Python library
