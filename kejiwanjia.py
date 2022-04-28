#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/9/12
import requests
import json
import logging
import os
import push
import sys

'''
cron: 50 8 * * * kejiwanjia.py
new Env('科技玩家签到');
'''

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("科技玩家")

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 ' \
     'Safari/537.36 Edg/97.0.1072.55 '


def login(username, password):
    login_url = 'https://www.kejiwanjia.com/wp-json/jwt-auth/v1/token'
    data = {
        'username': username,
        'password': password
    }
    headers = {
        'User-Agent': UA,
        'Referer': 'https://www.kejiwanjia.com/'
    }
    responseLogin = requests.post(login_url, data=data, headers=headers)
    try:
        token = responseLogin.json()['token']
        logger.info('登陆成功')
        return token
    except KeyError as e:
        error_message = responseLogin.json()['message'].split('：')[1]
        logger.error('登陆失败：%s', error_message)
        push.push('科技玩家', 'https://raw.githubusercontent.com/tanmx/checkin/main/icon/kejiwanjia.png', 1, error_message)
        return 1
       
def checkin(token):
    session = requests.session()
    mission_url = 'https://www.kejiwanjia.com/wp-json/b2/v1/getUserMission'
    checkin_url = 'https://www.kejiwanjia.com/wp-json/b2/v1/userMission'
    headers = {
        "Authorization": "Bearer " + token,
        'User-Agent': UA
    }
    # 需要先访问 https://www.kejiwanjia.com/wp-json/b2/v1/getUserMission 才能进行签到任务
    data = {
        'count': '5',
        'paged': '1'
    }
    logger.info('获取任务信息')
    session.post(mission_url, headers=headers, params=data)
    #签到
    responseCheckin = session.post(checkin_url, headers=headers)
    try:
        message = responseCheckin.json()
        pushMessage = "签到成功，获得 " + message['mission']['credit'] + " 积分，共计 " + message['mission']['my_credit'] + " 积分"
    except:
        pushMessage = '今日已签到，获得 ' + responseCheckin.json() + ' 积分'
    # message = {'date': '2022-01-25 15:35:58', 'credit': 98, 'mission': {'date': '2022-01-25 15:35:58', 'credit': '98', 'always': '1', 'tk': {'days': 0, 'credit': 0, 'bs': '2'}, 'my_credit': '298', 'current_user': 19348}}
    logger.info(pushMessage)
    push.push('科技玩家', 'https://raw.githubusercontent.com/tanmx/checkin/main/icon/kejiwanjia.png', 0, pushMessage)
    #push(pushMessage)

# def push(message):
#     push_url = 'https://api2.pushdeer.com/message/push'
#     payload = {'pushkey': 'PDU3747TBEFDPFJJpriXn3ibqxPEoF3JWJ6fxz9f', 'text': message}
#     try:
#         response = requests.get(push_url, params=payload)
#     except requests.RequestException as e:
#         logger.error(e)

def main():
    username = os.environ.get('KJWJ_USERNAME', None)
    password = os.environ.get('KJWJ_PASSWORD', None)
    token = login(username, password)
    if token != 1:
        checkin(token)

if __name__ == '__main__':
    main()