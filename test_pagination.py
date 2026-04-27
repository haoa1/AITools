#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from stock.stock import StockDataFetcher
import json

print("=" * 60)
print("测试分页获取所有股票")
print("=" * 60)

fetcher = StockDataFetcher()

# 测试获取所有股票
print("\n1. 测试获取所有A股:")
stocks = fetcher._get_eastmoney_stock_list(market='all')
print(f"总股票数量: {len(stocks)}")
if stocks:
    print(f"前5只股票:")
    for i, stock in enumerate(stocks[:5]):
        print(f"  {i+1}. {stock['symbol']} - {stock['name']}")
    
    # 统计市场分布
    sh_count = sum(1 for s in stocks if s['market'] == 'SH')
    sz_count = sum(1 for s in stocks if s['market'] == 'SZ')
    print(f"上海市场: {sh_count} 只")
    print(f"深圳市场: {sz_count} 只")

# 测试上海市场
print("\n2. 测试上海市场:")
stocks_sh = fetcher._get_eastmoney_stock_list(market='sh')
print(f"上海市场股票数量: {len(stocks_sh)}")
if stocks_sh:
    print(f"示例: {stocks_sh[0]['symbol']} - {stocks_sh[0]['name']}")

# 测试深圳市场
print("\n3. 测试深圳市场:")
stocks_sz = fetcher._get_eastmoney_stock_list(market='sz')
print(f"深圳市场股票数量: {len(stocks_sz)}")
if stocks_sz:
    print(f"示例: {stocks_sz[0]['symbol']} - {stocks_sz[0]['name']}")

# 测试通过get_all_china_stocks获取
print("\n4. 测试通过get_all_china_stocks获取:")
all_stocks = fetcher.get_all_china_stocks()
print(f"总股票数量: {len(all_stocks)}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)