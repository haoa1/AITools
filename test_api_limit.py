#!/usr/bin/env python3
import requests
import time

def test_page_size(page_size):
    """测试不同的每页数量"""
    url = 'http://push2.eastmoney.com/api/qt/clist/get'
    params = {
        'pn': 1,
        'pz': page_size,
        'po': 1,
        'np': 1,
        'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
        'fltt': 2,
        'invt': 2,
        'fid': 'f3',
        'fs': 'm:0+t:6,m:1+t:2,m:0+t:80,m:1+t:23',
        'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152',
        '_': str(int(time.time() * 1000))
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'http://quote.eastmoney.com/center/gridlist.html',
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'diff' in data['data']:
                stocks = data['data']['diff']
                total = data['data'].get('total', 0)
                return len(stocks), total
    except Exception as e:
        print(f"错误: {e}")
    
    return 0, 0

print("=" * 60)
print("测试东方财富API每页数量限制")
print("=" * 60)

# 测试不同的每页数量
test_sizes = [20, 50, 100, 200, 500, 1000, 2000]
for size in test_sizes:
    count, total = test_page_size(size)
    print(f"请求 {size:4d} 只，返回 {count:4d} 只，总计 {total}")
    time.sleep(1)

# 测试多页获取
print("\n测试多页获取:")
url = 'http://push2.eastmoney.com/api/qt/clist/get'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'http://quote.eastmoney.com/center/gridlist.html',
}

for page in [1, 2, 3, 4, 5]:
    params = {
        'pn': page,
        'pz': 100,
        'po': 1,
        'np': 1,
        'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
        'fltt': 2,
        'invt': 2,
        'fid': 'f3',
        'fs': 'm:0+t:6,m:1+t:2,m:0+t:80,m:1+t:23',
        'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152',
        '_': str(int(time.time() * 1000))
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'diff' in data['data']:
                stocks = data['data']['diff']
                total = data['data'].get('total', 0)
                print(f"第 {page} 页，请求 100 只，返回 {len(stocks)} 只")
                
                if stocks:
                    print(f"  示例: {stocks[0].get('f12', 'N/A')} - {stocks[0].get('f14', 'N/A')}")
    except Exception as e:
        print(f"第 {page} 页错误: {e}")
    
    time.sleep(1)