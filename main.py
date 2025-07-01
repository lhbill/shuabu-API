import requests
import random
import sys

def modify_steps(account, password, min_steps, max_steps, timeout=20):
    steps = random.randint(min_steps, max_steps)
    url = f"https://www.520113.xyz/api/shua?account={account}&password={password}&steps={steps}"
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        if result.get('status') == 'success':
            print(f"账号 {account[:3]}***{account[-3:]} 修改成功，步数：{steps}")
            return True
        else:
            print(f"账号 {account[:3]}***{account[-3:]} 修改失败，返回状态: {result}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}")
        return False
    except ValueError as e:
        print(f"解析 JSON 失败：{e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("错误：缺少账号或密码参数")
        print("用法: python main.py <账号> <密码>")
        sys.exit(1)
    
    min_steps = 4000
    max_steps = 5000
    account = sys.argv[1]
    password = sys.argv[2]
    
    modify_steps(account, password, min_steps, max_steps)