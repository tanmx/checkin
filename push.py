import os
import requests
from configparser import ConfigParser
import logging

cfg = ConfigParser()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("推送服务")

def load_config():
    config_path = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config'), 'push.ini')
    if os.path.exists(config_path):
        cfg.read(config_path, encoding='utf-8')
        return True
    else:
        return False

def title(checkin_name):
    return " checkin_name 签到："


# telegram的推送
def telegram(checkin_name, push_message):
    requests.post(
        url="https://{}/bot{}/sendMessage".format(cfg.get('telegram', 'api_url'), cfg.get('telegram', 'bot_token')),
        data={
            "chat_id": cfg.get('telegram', 'chat_id'),
            "text": title(status) + "\r\n" + push_message
        }
    )


# server酱
def ftqq(checkin_name, push_message):
    requests.post(
        url="https://sctapi.ftqq.com/{}.send".format(cfg.get('setting', 'push_token')),
        data={
            "title": title(checkin_name),
            "desp": push_message
        }
    )


# pushplus
def pushplus(checkin_name, push_message):
    requests.post(
        url="https://www.pushplus.plus/send",
        data={
            "token": cfg.get('setting', 'push_token'),
            "title": title(checkin_name),
            "content": push_message
        }
    )


# cq http协议的推送
def cqhttp(checkin_name, push_message):
    requests.post(
        url=cfg.get('cqhttp', 'cqhttp_url'),
        json={
            "user_id": cfg.getint('cqhttp', 'cqhttp_qq'),
            "message": title(checkin_name) + "\r\n" + push_message
        }
    )


# 企业微信 感谢linjie5492@github
def wecom(checkin_name, push_message):
    secret = cfg.get('wecom', 'secret')
    wechat_id = cfg.get('wecom', 'wechat_id')
    push_token = requests.post(
        url=f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={wechat_id}&corpsecret={secret}',
        data="").json()['access_token']
    push_data = {
        "agentid": cfg.get('wecom', 'agentid'),
        "msgtype": "text",
        "touser": "@all",
        "text": {
            "content": title(checkin_name) + "\r\n" + push_message
        }, "safe": 0}
    requests.post(f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={push_token}', json=push_data)


# pushdeer
def pushdeer(checkin_name, push_message):
    requests.get(
        url=f'{cfg.get("pushdeer", "api_url")}/message/push',
        params={
            "pushkey": cfg.get("pushdeer", "token"),
            "text": title(checkin_name),
            "desp": str(push_message).replace("\r\n", "\r\n\r\n"),
            "type": "markdown"
        }
    )


def push(checkin_name, push_message):
    if not load_config():
        return 0
    if cfg.getboolean('setting', 'enable'):
        push_server = cfg.get('setting', 'push_server').lower()
        logging.info("正在执行推送......")
        try:
            logging.debug(f"推送所用的服务为：{push_server}")
            eval(push_server[:10].lower() + "(checkin_name, push_message)")
        except NameError:
            logging.warning("推送服务名称错误")
        else:
            logging.info("推送完毕......")
    return 0