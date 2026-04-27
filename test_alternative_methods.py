#!/usr/bin/env python3
import requests
import time
import json

def test_method_1():
    """测试使用更简单的API"""
    print("方法1: 测试简化API...")
    url = "https://quote.eastmoney.com/center/api/sidemenu.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应类型: {type(data)}")
            return True
    except Exception as e:
        print(f"错误: {e}")
    return False

def test_method_2():
    """测试使用HTTP而不是HTTPS"""
    print("\n方法2: 测试HTTP API...")
    url = "http://quote.eastmoney.com/center/api/sidemenu.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应类型: {type(data)}")
            return True
    except Exception as e:
        print(f"错误: {e}")
    return False

def test_method_3():
    """测试直接获取页面然后解析"""
    print("\n方法3: 测试获取HTML页面...")
    url = "http://quote.eastmoney.com/center/gridlist.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应长度: {len(response.text)}")
        if response.status_code == 200:
            # 检查是否有股票数据
            if "股票代码" in response.text or "stock" in response.text.lower():
                print("页面包含股票数据")
                return True
    except Exception as e:
        print(f"错误: {e}")
    return False

def test_method_4():
    """测试其他财经网站"""
    print("\n方法4: 测试其他财经网站...")
    urls = [
        "http://hq.sinajs.cn/list=sh000001,sz399001",
        "http://qt.gtimg.cn/q=sh000001,sz399001",
        "https://xueqiu.com"
    ]
    
    for url in urls:
        print(f"\n测试: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"响应长度: {len(response.text)}")
                return True
        except Exception as e:
            print(f"错误: {type(e).__name__}")
    
    return False

def test_method_5():
    """测试网络连通性"""
    print("\n方法5: 测试基本网络连通性...")
    urls = [
        "http://baidu.com",
        "http://qq.com",
        "https://www.163.com"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"{url}: 状态码 {response.status_code}")
        except Exception as e:
            print(f"{url}: 连接失败 {type(e).__name__}")

print("=" * 60)
print("测试替代方法获取股票数据")
print("=" * 60)

# 测试网络连通性
test_method_5()

# 测试各种方法
methods = [test_method_1, test_method_2, test_method_3, test_method_4]
results = []

for method in methods:
    result = method()
    results.append(result)
    time.sleep(1)

print("\n" + "=" * 60)
print("测试结果总结:")
for i, result in enumerate(results):
    print(f"方法{i+1}: {'成功' if result else '失败'}")

# 如果有任何方法成功，尝试直接获取股票数据
if any(results):
    print("\n尝试直接获取股票数据...")
    test_stock_api()
else:
    print("\n所有方法都失败，网络可能有限制")

print("=" * 60)