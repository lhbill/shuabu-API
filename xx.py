# -*- coding: utf8 -*-
import datetime
import random
import sys
import time
import requests
import re

# 北京时间
time_bj = datetime.datetime.today() + datetime.timedelta(hours=8)
now = time_bj.strftime("%Y-%m-%d %H:%M:%S")
headers = {'User-Agent': 'MiFit/5.3.0 (iPhone; iOS 14.7.1; Scale/3.00)'}

def getBeijinTime():
    # 固定步数范围 18000-22000
    min_1 = 18000
    max_1 = 22000
    
    user_mi = sys.argv[1]
    passwd_mi = sys.argv[2]
    user_list = user_mi.split('#')
    passwd_list = passwd_mi.split('#')
    
    if len(user_list) == len(passwd_list):
        msg_mi = ""
        for user_mi, passwd_mi in zip(user_list, passwd_list):
            msg_mi += main(user_mi, passwd_mi, min_1, max_1)
    else:
        print("账号和密码数量不匹配")

def get_code(location):
    code_pattern = re.compile("(?<=access=).*?(?=&)")
    return code_pattern.findall(location)[0]

def login(user, password):
    url1 = f"https://api-user.huami.com/registrations/{user}/tokens"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2"
    }
    data1 = {
        "client_id": "HuaMi",
        "password": password,
        "redirect_uri": "https://s3-us-west-2.amazonaws.com/hm-registration/successsignin.html",
        "token": "access"
    }
    r1 = requests.post(url1, data=data1, headers=headers, allow_redirects=False)
    location = r1.headers["Location"]
    try:
        code = get_code(location)
    except:
        return 0, 0
        
    url2 = "https://account.huami.com/v2/client/login"
    data2 = {
        "allow_registration=": "false",
        "app_name": "com.xiaomi.hm.health",
        "app_version": "6.3.5",
        "code": code,
        "country_code": "CN",
        "device_id": "2C8B4939-0CCD-4E94-8CBA-CB8EA6E613A1",
        "device_model": "phone",
        "dn": "api-user.huami.com,api-mifit.huami.com,app-analytics.huami.com",
        "grant_type": "access_token",
        "lang": "zh_CN",
        "os_version": "1.5.0",
        "source": "com.xiaomi.hm.health",
        "third_name": "email",
    }
    r2 = requests.post(url2, data=data2, headers=headers).json()
    token_info = r2["token_info"]
    return token_info["login_token"], token_info["user_id"]

def main(_user, _passwd, min_1, max_1):
    user = str(_user)
    password = str(_passwd)
    step = random.randint(min_1, max_1)
    print(f"已设置为随机步数({min_1}~{max_1})")
    
    if not user or not password:
        print("用户名或密码不能为空！")
        return "login fail!"
    
    login_token, userid = login(user, password)
    if login_token == 0:
        print("登陆失败！")
        return "login fail!"

    t = int((datetime.datetime.utcnow() + datetime.timedelta(hours=8)).timestamp() * 1000)
    app_token = get_app_token(login_token)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # 原始数据模板（此处为缩短示例，实际使用时保持原长字符串）
    data_json = '原始长字符串保持不变'
    
    # 直接替换日期和步数
    data_json = data_json.replace('2021-08-07', today)
    data_json = data_json.replace('18272', str(step))
    
    url = f'https://api-mifit-cn.huami.com/v1/data/band_data.json?&t={t}'
    head = {
        "apptoken": app_token,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = f'userid={userid}&last_sync_data_time=1597306380&device_type=0&last_deviceid=DA932FFFFE8816E7&data_json={data_json}'

    response = requests.post(url, data=data, headers=head).json()
    result = f"[{now}]\n\n{user[:3]}****{user[7:]} 已成功修改（{step}）步\\[" + response['message'] + "]\n\n"
    print(result)
    return result

def get_app_token(login_token):
    url = f"https://account-cn.huami.com/v1/client/app_tokens?app_name=com.xiaomi.hm.health&dn=api-user.huami.com,api-mifit.huami.com,app-analytics.huami.com&login_token={login_token}"
    try:
        response = requests.get(url, headers=headers, timeout=5).json()
        return response['token_info']['app_token']
    except:
        print("获取app_token失败")
        return None

def main_handler(event, context):
    getBeijinTime()

if __name__ == "__main__":
    getBeijinTime()