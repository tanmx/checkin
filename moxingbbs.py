# -*- coding: utf-8 -*-
import requests
import re
import json
import logging
import os
import hashlib
import push
'''
cron: 51 8 * * * moxingbbs.py
new Env('MX论坛签到');
'''
#https://blog.homurax.com/2020/01/13/discuz-login/
#https://gist.github.com/ficapy/11130233

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MX论坛")

URL = 'https://moxing.institute'

class MXcheckin:
    def __init__(self, username, password):
        self.session = requests.session()
        self.url = URL
        self.username = username
        self.password = password

    def md5(self, password):
        return hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()

    def user_login(self):
        password = self.md5(self.password)
        #先获取 loginhash 和 formhash
        loginhash, formhash = self.form_hash()
        login_url = self.url + '/member.php?mod=logging&action=login&loginsubmit=yes&frommessage&loginhash=' + loginhash + '&inajax=1'
        fromData = {
            'formhash': formhash,
            'referer': URL,
            'loginfield': 'username',
            'username': self.username,
            'password': password,
            'questionid': 0,
            'answer': ''
        }
        login_rst = self.session.post(login_url, data=fromData)
        #logger.info('%s', login_rst.cookies)
        if re.search(u'现在将转入登录前页面',login_rst.text):
            logger.info('%s 登陆成功', username)
        #    logger.info('%s', session.cookies.get_dict())
        else:
            logger.error('登陆失败')
            push.push('moxingbbs', 'https://day.app/assets/images/avatar.jpg', 1, '登陆失败')

    def form_hash(self):
        rst = self.session.get( self.url + '/member.php?mod=logging&action=login').text
        loginhash = re.search(r'<div id="main_messaqge_(.+?)">', rst).group(1)
        formhash = re.search(r'<input type="hidden" name="formhash" value="(.+?)" />', rst).group(1)
        return loginhash, formhash
    
    def user_info(self):
        user_info = self.session.get(self.url + '/home.php?mod=spacecp&ac=credit').text
        #logger.info('%s', user_info)
        total_rmb = re.search(r'软妹币: </em>(\d+).+?</li>', user_info).group(1)
        today_add = re.search(r'软妹币 <span class="xi1">\+(\d+)</span></td>', user_info).group(1)
        #logger.info('%s,%s', total_rmb, today_add)
        return total_rmb, today_add

    def checkin(self):
        self.user_login()
        #formhash使用一次失效。重新获取
        headers = {
             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
        #     'cookie': '"dyHK_3864_auth": "9cecL5CZ9WTw%2ByyIpQIJKwmTEgJ4xeSgUhCV4uNjzrw9Vmr4cXusJt5ibbHWtNZuWOmc6uda0D3YcycCI4Vs4DHLTA", "dyHK_3864_checkfollow": "1", "dyHK_3864_lastact": "1650792261%09member.php%09logging", "dyHK_3864_lastcheckfeed": "75796%7C1650792261", "dyHK_3864_lastvisit": "1650788661", "dyHK_3864_lip": "101.34.119.114%2C1650792088", "dyHK_3864_saltkey": "kg774mcr", "dyHK_3864_sid": "OOJ9f3", "dyHK_3864_ulastactivity": "26f4SmdbhA%2FSueOJn84dbRTWNPeS0IM7N3vCvbrm2uyQPkPjL1U5"'
         }
        
        rst = self.session.get( self.url + '/member.php?mod=logging&action=login').text
        formhash = re.search(r'<input type="hidden" name="formhash" value="(.+?)" />', rst).group(1)
        formData = {
            'id': 'k_misign:sign',
            'operation': 'qiandao',
            'format': 'global_usernav_extra',
            'formhash': formhash,
            'inajax': '1',
            'ajaxtarget': 'k_misign_topb'
        }
        checkin_url = self.url + '/plugin.php?id=k_misign:sign'
        checkin_rst = self.session.post(checkin_url, headers=headers, data=formData)
        if re.search(u'今日已签',checkin_rst.text):
            logger.info('%s 签到成功', username)
            #logger.info('%s', checkin_rst.text)
            total_rmb, today_add = self.user_info()
            message = username + ' 签到成功，今日软妹币：+' + today_add + ' 软妹币共有：' + total_rmb
            logger.info('开始消息推送')
            push.push('moxingbbs', 'https://day.app/assets/images/avatar.jpg', 0, message)
            logger.info('%s', message)
        else:
            push.push('moxingbbs', 'https://day.app/assets/images/avatar.jpg', 1, '签到失败')
            logger.error('签到失败')
        
        
if __name__ == '__main__':
    username = ''
    password = ''
    if username is None or password is None:
        logger.info('未配置登陆信息，尝试从环境变量获取……')
        username = os.environ.get('MX_USERNAME', None)
        password = os.environ.get('MX_PASSWORD', None)
    MXcheckin(username, password).checkin()