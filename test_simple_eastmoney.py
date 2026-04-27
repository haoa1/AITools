#!/usr/bin/env python3
import requests
import time

def test_simple_request():
    """测试更简单的请求"""
    print("测试东方财富API...")
    
    # 简单的请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # 测试不同的API端点
    test_urls = [
        "http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=20&fs=m:0+t:6,m:1+t:2,m:0+t:80,m:1+t:23&fields=f12,f13,f14",
        "http://quote.eastmoney.com/stock_list.html",
        "http://quote.eastmoney.com/sh_list.html",
        "http://quote.eastmoney.com/sz_list.html"
    ]
    
    for url in test_urls:
        print(f"\n测试: {url[:80]}...")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"状态码: {response.status_code}")
            print(f"内容类型: {response.headers.get('Content-Type', 'unknown')}")
            
            if response.status_code == 200:
                content = response.text[:500]
                print(f"前500字符: {content}")
                
                # 检查是否包含股票数据
                if "股票" in content or "stock" in content.lower() or "f12" in content:
                    print("✓ 看起来包含股票数据")
                    return url
        except Exception as e:
            print(f"错误: {type(e).__name__}: {str(e)[:100]}")
        
        time.sleep(1)
    
    return None

def test_alternative_source():
    """测试替代数据源"""
    print("\n\n测试替代数据源...")
    
    # 尝试使用其他财经网站
    sources = [
        # 网易财经
        ("网易财经", "http://quotes.money.163.com/hs/service/diyrank.php?page=0&query=STYPE:EQA&fields=SYMBOL,SNAME&count=20"),
        # 雪球（可能需要更复杂的请求）
        ("雪球", "https://xueqiu.com/hq"),
    ]
    
    for name, url in sources:
        print(f"\n测试 {name}: {url[:80]}...")
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text[:500]
                print(f"内容长度: {len(response.text)}")
                
                # 检查是否包含股票代码
                if "SYMBOL" in content or "SNAME" in content or "股票" in content:
                    print("✓ 可能包含股票数据")
                    return name, url
        except Exception as e:
            print(f"错误: {type(e).__name__}")
        
        time.sleep(1)
    
    return None

if __name__ == "__main__":
    print("=" * 60)
    print("测试股票数据源")
    print("=" * 60)
    
    # 测试东方财富
    result = test_simple_request()
    
    if result:
        print(f"\n✓ 找到可用的API: {result}")
    else:
        print("\n✗ 东方财富API测试失败")
        
        # 测试其他数据源
        alt_result = test_alternative_source()
        if alt_result:
            print(f"\n✓ 找到替代数据源: {alt_result[0]}")
            print(f"URL: {alt_result[1]}")
        else:
            print("\n✗ 没有找到可用的股票数据源")
            
            print("\n建议:")
            print("1. 检查网络连接")
            print("2. 尝试安装tushare: pip install tushare")
            print("3. 使用本地股票数据文件")
            print("4. 联系用户确认需求")