#!/usr/bin/python
import requests
import json
import time
import hmac
import hashlib
import base64
import urllib.parse

def gettssign():
    _timestamp = str(round(time.time() * 1000))
    _secret = 'SEC4bdeb53ccdce05e1fd4d6c5c1033ce1c3ccdea4580aae9a95736809e33bbb264'
    _secret_enc = _secret.encode('utf-8')
    _string_to_sign = '{}\n{}'.format(_timestamp, _secret)
    _string_to_sign_enc = _string_to_sign.encode('utf-8')
    hmac_code = hmac.new(_secret_enc, _string_to_sign_enc, digestmod=hashlib.sha256).digest()
    _sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return "&timestamp=%s&sign=%s"%(_timestamp, _sign)

def dingmessage():
# 请求的URL，WebHook地址
    webhook = "https://oapi.dingtalk.com/robot/send?access_token=ab04c79b84d354f7f8464547d71aa8595b3ccd7d7f0381e65e62ccab14377534"
#构建请求头部
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
#构建请求数据
    txtitle = "不满意工单派发通知"
    message ={
        "msgtype": "markdown",
        "markdown": {
            "title": txtitle,
            "text" : "#### 工单派发通知 @19976970945 \n> 不满意工单已通过智慧装维软件派单到班长\n> 此类必须由装维班长上门落实处理不满意原因，并总结分析发维护事业部群。严禁再派发到包区装维人员处理。\n"
        },
        "at": {
            "atMobiles": [
                '18692060908',
                '19976970945'
            ],
            "isAtAll": False
        }
    }
#对请求的数据进行json封装
    message_json = json.dumps(message)
#发送请求
    info = requests.post(url=webhook+gettssign(),data=message_json,headers=header)
#打印返回的结果
    print(info.text)

if __name__=="__main__":
    dingmessage()