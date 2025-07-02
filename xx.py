# -*- coding: utf8 -*-
import datetime
import json
import random
import re
import sys
import time
import requests
from datetime import timezone, timedelta

# 获取 UTC+8 时区对象
tz_bj = timezone(timedelta(hours=8))
headers = {'User-Agent': 'MiFit/6.3.5 (iPhone; iOS 16.0; Scale/3.00)'}


def get_utc8_time():
    """获取UTC+8格式的当前时间（用于日志和日期替换）"""
    now_bj = datetime.now(tz_bj)
    return now_bj.strftime("%Y-%m-%d %H:%M:%S"), now_bj


def get_utc8_timestamp():
    """获取UTC+8时区的时间戳（毫秒级，用于接口请求）"""
    return int(datetime.now(tz_bj).timestamp() * 1000)


def sync_server_time():
    """同步服务器时间（失败则返回本地时间）"""
    try:
        # 示例接口，实际需确认可用接口
        response = requests.get("https://api-mifit-cn.huami.com/v1/time", headers=headers)
        return response.json().get("server_time", get_utc8_timestamp())
    except:
        print("[警告] 服务器时间同步失败，使用本地时间")
        return get_utc8_timestamp()


def get_code(location):
    """从重定向URL中提取授权码"""
    try:
        code_pattern = re.compile("(?<=access=).*?(?=&)")
        return code_pattern.findall(location)[0]
    except Exception as e:
        print(f"[错误] 提取授权码失败: {str(e)}")
        return None


def login(user, password):
    """登录获取login_token和userid"""
    print(f"[登录流程] 开始处理用户: {user[:3]}****{user[-3:]}")
    
    # 第一步：获取重定向地址
    url1 = f"https://api-user.huami.com/registrations/{user}/tokens"
    headers_login = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "User-Agent": headers["User-Agent"],
        "X-App-Id": "HuaMi"
    }
    data1 = {
        "client_id": "HuaMi",
        "password": password,
        "redirect_uri": "https://s3-us-west-2.amazonaws.com/hm-registration/successsignin.html",
        "response_type": "token"
    }
    
    try:
        r1 = requests.post(url1, data=data1, headers=headers_login, allow_redirects=False, timeout=10)
        print(f"[第一步] 响应状态: {r1.status_code}")
        
        if "Location" not in r1.headers:
            print(f"[第一步失败] 未获取到重定向地址，响应内容: {r1.text[:200]}...")
            return 0, 0
            
        location = r1.headers["Location"]
        print(f"[第一步成功] 重定向地址已获取")
    except Exception as e:
        print(f"[第一步异常] 错误: {str(e)}")
        return 0, 0

    # 第二步：提取授权码并获取登录令牌
    try:
        code = get_code(location)
        if not code:
            print("[第二步失败] 授权码提取失败")
            return 0, 0
            
        url2 = "https://account.huami.com/v2/client/login"
        device_id = str(uuid.uuid4()).upper()  # 随机生成设备ID
        data2 = {
            "allow_registration": "false",
            "app_name": "com.xiaomi.hm.health",
            "app_version": "6.3.5",
            "code": code,
            "country_code": "CN",
            "device_id": device_id,
            "device_model": "phone",
            "dn": "api-user.huami.com,api-mifit.huami.com,app-analytics.huami.com",
            "grant_type": "access_token",
            "lang": "zh_CN",
            "os_version": "14.7.1",  # 匹配iOS版本
            "source": "com.xiaomi.hm.health",
            "third_name": "email",
        }
        
        r2 = requests.post(url2, data=data2, headers=headers_login, timeout=10).json()
        print(f"[第二步] 响应状态: 成功获取登录信息")
        
        login_token = r2["token_info"]["login_token"]
        userid = r2["token_info"]["user_id"]
        return login_token, userid
        
    except KeyError as e:
        print(f"[第二步失败] 响应格式错误，缺少字段: {str(e)}")
        print(f"[调试信息] 响应内容: {r2}")
        return 0, 0
    except Exception as e:
        print(f"[第二步异常] 错误: {str(e)}")
        return 0, 0


def get_app_token(login_token):
    """获取app_token"""
    url = f"https://account-cn.huami.com/v1/client/app_tokens?app_name=com.xiaomi.hm.health&dn=api-user.huami.com,api-mifit.huami.com,app-analytics.huami.com&login_token={login_token}"
    for retry in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=5).json()
            return response['token_info']['app_token']
        except requests.exceptions.ConnectTimeout:
            print(f"[重试] 请求超时，第 {retry+1} 次重试...")
        except Exception as e:
            print(f"[错误] 获取app_token失败: {str(e)}")
    return None


def submit_step_data(userid, app_token, step, today):
    """提交步数数据（长字符串已忽略，保留逻辑框架）"""
    print(f"[步数提交] 用户: {userid[:8]}****，步数: {step}")
    
    # 注意：此处省略data_json长字符串处理，实际需保留或从文件加载
    t = sync_server_time()
    url = f'https://api-mifit-cn.huami.com/v1/data/band_data.json?&t={t}'
    head = {
        "apptoken": app_token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # 示例数据（实际需替换为正确的data_json）
    data = f'userid={userid}&last_sync_data_time=1597306380&device_type=0&last_deviceid=DA932FFFFE8816E7&data_json=...'
    
    try:
        response = requests.post(url, data=data, headers=head, timeout=10).json()
        print(f"[提交结果] 状态: {response['message']}")
        return f"[成功] 步数 {step} 提交完成"
    except Exception as e:
        print(f"[提交失败] 错误: {str(e)}")
        return f"[失败] 步数提交异常"


def main(_user, _passwd, min_step, max_step):
    """主函数"""
    user = str(_user)
    password = str(_passwd)
    step = random.randint(min_step, max_step)
    now_str, now_bj = get_utc8_time()
    today = now_bj.strftime("%Y-%m-%d")
    
    print(f"[任务开始] 时间: {now_str}，用户: {user[:3]}****{user[-3:]}，步数: {step}")
    
    if not user or not password:
        print("[错误] 用户名或密码为空")
        return "login fail!"
    
    login_token, userid = login(user, password)
    if login_token == 0:
        print("[错误] 登录失败，终止任务")
        return "login fail!"
    
    app_token = get_app_token(login_token)
    if not app_token:
        print("[错误] 获取app_token失败，终止任务")
        return "app_token fail"
    
    result = submit_step_data(userid, app_token, step, today)
    return result


def getBeijinTime():
    """入口函数"""
    try:
        print("[系统启动] 开始执行步数提交任务")
        if len(sys.argv) < 3:
            print("[错误] 请输入用户名和密码，格式: python script.py user#user2 pass#pass2")
            return
        
        user_mi = sys.argv[1]
        passwd_mi = sys.argv[2]
        user_list = user_mi.split('#')
        passwd_list = passwd_mi.split('#')
        
        if len(user_list) != len(passwd_list):
            print("[错误] 用户名和密码数量不匹配")
            return
        
        min_step = 2500
        max_step = 3000
        print(f"[参数设置] 步数范围: {min_step}~{max_step}")
        
        for user, passwd in zip(user_list, passwd_list):
            main(user, passwd, min_step, max_step)
            
    except Exception as e:
        print(f"[系统异常] 任务终止: {str(e)}")


if __name__ == "__main__":
    getBeijinTime()