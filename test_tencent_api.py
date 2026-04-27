#!/usr/bin/env python3
import requests

# 测试腾讯财经API
url = "http://qt.gtimg.cn/q=sh000001,sz399001"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'http://qt.gtimg.cn/'
}

response = requests.get(url, headers=headers, timeout=10)
print(f"状态码: {response.status_code}")
print(f"响应内容:")
print(response.text[:500])
print("...")
print(response.text[-500:])

# 分析响应格式
print("\n分析响应格式:")
lines = response.text.strip().split('\n')
for i, line in enumerate(lines):
    print(f"行 {i+1}: {line[:100]}")

# 尝试获取股票列表
print("\n尝试获取更多股票...")
# 常见股票代码
test_codes = ["sh000001", "sz000002", "sh600000", "sz300001"]
url_multi = f"http://qt.gtimg.cn/q={','.join(test_codes)}"
response2 = requests.get(url_multi, headers=headers, timeout=10)
print(f"多股票状态码: {response2.status_code}")
lines2 = response2.text.strip().split('\n')
for i, line in enumerate(lines2):
    print(f"股票 {test_codes[i]}: {line[:200]}")