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


def title(status):
    if status == 0:
        return "签到成功!"
    elif status == 1:
        return "签到失败!"

# pushdeer
# def pushdeer(checkin_name, push_message):
#     requests.get(
#         url=f'{cfg.get("pushdeer", "api_url")}/message/push',
#         params={
#             "pushkey": cfg.get("pushdeer", "token"),
#             "text": title(checkin_name),
#             "desp": str(push_message).replace("\r\n", "\r\n\r\n"),
#             "type": "markdown"
#         }
#     )

def bark(checkin_name, img_url, status, push_message):
    requests.get(
        url=f'{cfg.get("bark", "api_url")}/{cfg.get("bark", "token")}/{checkin_name}: {title(status)}/{push_message}',
        params={
            "icon": img_url
        }
    )

def push(checkin_name, img_url, status, push_message):
    if not load_config():
        return 0
    if cfg.getboolean('setting', 'enable'):
        push_server = cfg.get('setting', 'push_server').lower()
        logger.info("正在执行推送......")
        try:
            logger.debug(f"推送所用的服务为：{push_server}")
            eval(push_server[:10].lower() + "(checkin_name, img_url, status, push_message)")
        except NameError:
            logger.warning("推送服务名称错误")
        else:
            logger.info("推送完毕......")
    return 0