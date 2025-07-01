import requests
import random

# 执行步数修改操作
def modify_steps(account, password, min_steps, max_steps, timeout=20):
    steps = random.randint(min_steps, max_steps)
    url = f"https://www.520113.xyz/api/shua?account={account}&password={password}&steps={steps}"
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # 检查 HTTP 状态码
        result = response.json()
        if result.get('status') =='success':
            print(f"账号 {account[:3]}***{account[-3:]} 修改成功，步数：{steps}")
            return f"账号 {account[:3]}***{account[-3:]} 修改成功，步数：{steps}"
        else:
            print(f"账号 {account[:3]}***{account[-3:]} 修改失败，返回状态不为 success")
            return f"账号 {account[:3]}***{account[-3:]} 修改失败，返回状态不为 success"
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}")
        return f"账号 {account[:3]}***{account[-3:]} 请求失败：{e}"
    except ValueError as e:
        print(f"解析 JSON 失败：{e}")
        return f"账号 {account[:3]}***{account[-3:]} 解析 JSON 失败：{e}"

if __name__ == "__main__":
    min_steps = 4000
    max_steps = 5000
    account = "账号"  # 请替换为实际账号
    password = "密码"  # 请替换为实际密码
    modify_steps(account, password, min_steps, max_steps)
