# -*- coding: utf8 -*-
import datetime
from datetime import timezone, timedelta
import random
import sys

# 北京时间 (UTC+8)
tz_bj = timezone(timedelta(hours=8))
time_bj = datetime.datetime.now(tz_bj)
now = time_bj.strftime("%Y-%m-%d %H:%M:%S")

# 获取北京时间确定随机步数&启动主函数
def getBeijinTime():
    # 使用正确的北京时间
    now_bj = datetime.datetime.now(tz_bj)
    now = now_bj.strftime("%Y-%m-%d %H:%M:%S")
    print(f"当前北京时间: {now}")
    
    # 设置步数范围（示例范围：900~1000）
    min_step = 900
    max_step = 1000
    print(f"步数范围设置为: {min_step}~{max_step}")

    if min_step <= 0 or max_step <= 0:
        print("当前主人设置了0步数呢，本次不提交")
        return

    # 简化参数获取逻辑（仅保留示例逻辑）
    if len(sys.argv) < 3:
        print("请输入用户名和密码参数")
        return
    
    user_mi = sys.argv[1]
    passwd_mi = sys.argv[2]
    
    # 处理多用户逻辑（简化示例）
    user_list = user_mi.split('#')
    passwd_list = passwd_mi.split('#')
    
    if len(user_list) != len(passwd_list):
        print("用户名和密码数量不匹配")
        return
    
    # 主流程（简化为打印）
    for user, pwd in zip(user_list, passwd_list):
        # 生成随机步数
        step = random.randint(min_step, max_step)
        print(f"用户 {user[:3]}****{user[7:]} 设置今日步数: {step}")
        print(f"日期: {now.split(' ')[0]}, 时间: {now.split(' ')[1]}, 步数: {step}")

def main_handler(event, context):
    getBeijinTime()

if __name__ == "__main__":
    getBeijinTime()