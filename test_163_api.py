#!/usr/bin/env python3
import requests
import json

url = "http://quotes.money.163.com/hs/service/diyrank.php?page=0&query=STYPE:EQA&fields=SYMBOL,SNAME&count=20"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers, timeout=10)
print(f"状态码: {response.status_code}")
print(f"响应长度: {len(response.text)}")
print(f"响应内容前500字符:")
print(response.text[:500])
print("...")
print(response.text[-500:])

# 尝试解析JSON
if response.text.strip():
    try:
        data = json.loads(response.text)
        print(f"\nJSON解析成功:")
        print(f"数据类型: {type(data)}")
        print(f"数据键: {list(data.keys())}")
        
        if 'list' in data:
            print(f"列表长度: {len(data['list'])}")
            for i, item in enumerate(data['list'][:5]):
                print(f"  股票{i+1}: {item}")
    except json.JSONDecodeError:
        print(f"\nJSON解析失败，可能是HTML页面")
        
        # 检查是否是HTML
        if "<html" in response.text.lower() or "<title>" in response.text.lower():
            print("响应是HTML页面，可能有访问限制")
            
            # 提取标题
            import re
            title_match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
            if title_match:
                print(f"页面标题: {title_match.group(1)}")