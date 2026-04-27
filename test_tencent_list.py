#!/usr/bin/env python3
import requests
import time

def test_get_stock_list():
    """测试获取股票列表"""
    # 尝试腾讯财经的股票列表API
    # 根据网上资料，可能有以下API：
    # 1. http://qt.gtimg.cn/q=szA,shA 获取全部A股（可能有限制）
    # 2. http://quote.tool.hexun.com/hqzx/quote.aspx?market=3&sorttype=3&updown=up&page=1&count=20
    # 3. 使用sina的hs_a接口
    
    print("测试各种股票列表API...")
    
    # 测试1: 腾讯全部A股（可能无效）
    print("\n1. 测试腾讯全部A股API...")
    url1 = "http://qt.gtimg.cn/q=szA,shA"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'http://qt.gtimg.cn/'
    }
    
    try:
        response = requests.get(url1, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"响应长度: {len(response.text)}")
            print(f"前200字符: {response.text[:200]}")
    except Exception as e:
        print(f"错误: {e}")
    
    time.sleep(1)
    
    # 测试2: 和讯财经
    print("\n2. 测试和讯财经API...")
    url2 = "http://quote.tool.hexun.com/hqzx/quote.aspx?market=3&sorttype=3&updown=up&page=1&count=50"
    try:
        response = requests.get(url2, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"响应长度: {len(response.text)}")
            print(f"前300字符: {response.text[:300]}")
    except Exception as e:
        print(f"错误: {e}")
    
    time.sleep(1)
    
    # 测试3: 新浪HS_A接口
    print("\n3. 测试新浪HS_A接口...")
    url3 = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=50&sort=symbol&asc=1&node=hs_a"
    try:
        response = requests.get(url3, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"响应长度: {len(response.text)}")
            if response.text and len(response.text) > 10:
                print(f"内容示例: {response.text[:500]}")
                return True
    except Exception as e:
        print(f"错误: {e}")
    
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("测试股票列表API")
    print("=" * 60)
    
    success = test_get_stock_list()
    
    if success:
        print("\n找到了可用的股票列表API！")
    else:
        print("\n没有找到可用的股票列表API，需要考虑其他方法")