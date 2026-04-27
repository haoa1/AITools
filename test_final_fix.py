#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from stock.stock import StockDataFetcher

print("=" * 60)
print("测试修复后的get_all_china_stocks函数")
print("=" * 60)

fetcher = StockDataFetcher()

# 测试获取所有股票
print("\n1. 测试get_all_china_stocks（所有市场，默认eastmoney）:")
all_stocks = fetcher.get_all_china_stocks()
print(f"总股票数量: {len(all_stocks)}")

# 统计市场分布
if all_stocks:
    sh_count = sum(1 for s in all_stocks if s['market'] == 'SH')
    sz_count = sum(1 for s in all_stocks if s['market'] == 'SZ')
    print(f"上海市场: {sh_count} 只")
    print(f"深圳市场: {sz_count} 只")
    
    print(f"\n前10只股票:")
    for i, stock in enumerate(all_stocks[:10]):
        print(f"  {i+1:2d}. {stock['symbol']} - {stock['name']}")

# 测试上海市场
print("\n2. 测试get_all_china_stocks（仅上海市场）:")
sh_stocks = fetcher.get_all_china_stocks(market='sh')
print(f"上海市场股票数量: {len(sh_stocks)}")
if sh_stocks:
    print("前5只:")
    for i, stock in enumerate(sh_stocks[:5]):
        print(f"  {stock['symbol']} - {stock['name']}")

# 测试深圳市场
print("\n3. 测试get_all_china_stocks（仅深圳市场）:")
sz_stocks = fetcher.get_all_china_stocks(market='sz')
print(f"深圳市场股票数量: {len(sz_stocks)}")
if sz_stocks:
    print("前5只:")
    for i, stock in enumerate(sz_stocks[:5]):
        print(f"  {stock['symbol']} - {stock['name']}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)