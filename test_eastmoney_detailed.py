#!/usr/bin/env python3
import requests
import json
import time

def get_eastmoney_stocks_page(page=1, page_size=100, market='all'):
    """获取东方财富股票列表（单页）"""
    
    # 市场映射
    market_map = {
        'sh': 'm:1+t:2,m:1+t:23',  # 上海主板+科创板
        'sz': 'm:0+t:6,m:0+t:80',  # 深圳主板+创业板
        'all': 'm:0+t:6,m:1+t:2,m:0+t:80,m:1+t:23'  # 全部A股
    }
    
    fs = market_map.get(market, market_map['all'])
    
    url = 'http://push2.eastmoney.com/api/qt/clist/get'
    params = {
        'pn': page,
        'pz': page_size,
        'po': 1,
        'np': 1,
        'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
        'fltt': 2,
        'invt': 2,
        'fid': 'f3',
        'fs': fs,
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
            return response.json()
    except Exception as e:
        print(f"获取数据失败: {e}")
    
    return None

def test_field_mapping():
    """测试字段映射"""
    print("=" * 60)
    print("东方财富API字段解析")
    print("=" * 60)
    
    data = get_eastmoney_stocks_page(page=1, page_size=5, market='all')
    
    if data and 'data' in data and 'diff' in data['data']:
        stocks = data['data']['diff']
        
        print(f"返回字段数量: {len(stocks[0].keys()) if stocks else 0}")
        print("\n字段映射:")
        
        # 根据东方财富API文档的字段映射
        field_map = {
            'f12': '股票代码',
            'f13': '市场类型',  # 0:深圳，1:上海
            'f14': '股票名称',
            'f2': '最新价',
            'f3': '涨跌幅',
            'f4': '涨跌额',
            'f5': '成交量',
            'f6': '成交额',
            'f7': '振幅',
            'f8': '换手率',
            'f9': '市盈率',
            'f10': '量比',
            'f15': '最高价',
            'f16': '最低价',
            'f17': '开盘价',
            'f18': '昨收价',
            'f20': '总市值',
            'f21': '流通市值',
            'f23': '市净率',
        }
        
        if stocks:
            sample = stocks[0]
            print("\n示例股票数据:")
            for key, value in sample.items():
                chinese_name = field_map.get(key, '未知')
                print(f"  {key}({chinese_name}): {value}")
            
            # 显示股票总数
            total = data['data'].get('total', 0)
            print(f"\n总股票数量: {total}")
            
            return total
    else:
        print("获取数据失败")
    
    return 0

def get_all_stocks_test():
    """测试获取所有股票"""
    print("\n" + "=" * 60)
    print("测试获取所有股票")
    print("=" * 60)
    
    # 先获取第一页了解总数
    data = get_eastmoney_stocks_page(page=1, page_size=20, market='all')
    if data and 'data' in data:
        total = data['data'].get('total', 0)
        print(f"总股票数量: {total}")
        
        # 获取第一页数据
        stocks = data['data'].get('diff', [])
        print(f"当前页股票数量: {len(stocks)}")
        
        # 显示前几个股票
        print("\n前10只股票:")
        for i, stock in enumerate(stocks[:10]):
            code = stock.get('f12', '')
            name = stock.get('f14', '')
            market_code = stock.get('f13', '')
            market = '上海' if market_code == 1 else '深圳'
            print(f"  {i+1}. {code} ({market}) - {name}")
        
        return total
    else:
        print("获取数据失败")
        return 0

def test_market_filter():
    """测试市场筛选"""
    print("\n" + "=" * 60)
    print("测试市场筛选")
    print("=" * 60)
    
    for market in ['sh', 'sz', 'all']:
        print(f"\n市场: {market}")
        data = get_eastmoney_stocks_page(page=1, page_size=5, market=market)
        if data and 'data' in data:
            total = data['data'].get('total', 0)
            stocks = data['data'].get('diff', [])
            print(f"  总数量: {total}")
            if stocks:
                for i, stock in enumerate(stocks[:3]):
                    code = stock.get('f12', '')
                    name = stock.get('f14', '')
                    print(f"  示例{i+1}: {code} - {name}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    total = test_field_mapping()
    get_all_stocks_test()
    test_market_filter()
    
    print("\n" + "=" * 60)
    print("结论:")
    print("=" * 60)
    print("1. 东方财富API可用，可以获取股票列表")
    print("2. 支持市场筛选（上海、深圳、全部）")
    print("3. 需要分页获取所有股票")
    print("4. 股票总数可通过total字段获取")
    print("5. 市场类型: f13=1（上海），f13=0（深圳）")