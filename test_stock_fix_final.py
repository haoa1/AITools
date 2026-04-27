#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from stock.stock import get_all_china_stocks, StockDataFetcher
import json

print("=" * 60)
print("测试修复后的股票列表功能")
print("=" * 60)

# 测试1: 默认参数（应该使用东方财富）
print("\n1. 测试默认参数（东方财富数据源）:")
result = get_all_china_stocks()
try:
    stocks = json.loads(result)
    print(f"  返回股票数量: {len(stocks)}")
    print(f"  前3只股票:")
    for i, stock in enumerate(stocks[:3]):
        print(f"    {i+1}. {stock['symbol']} - {stock['name']}")
except:
    print(f"  结果: {result[:200]}...")

# 测试2: 上海市场
print("\n2. 测试上海市场（东方财富）:")
result = get_all_china_stocks(market='sh')
try:
    stocks = json.loads(result)
    print(f"  上海市场股票数量: {len(stocks)}")
    if stocks:
        print(f"  示例: {stocks[0]['symbol']} - {stocks[0]['name']}")
except:
    print(f"  结果: {result[:200]}...")

# 测试3: 深圳市场
print("\n3. 测试深圳市场（东方财富）:")
result = get_all_china_stocks(market='sz')
try:
    stocks = json.loads(result)
    print(f"  深圳市场股票数量: {len(stocks)}")
    if stocks:
        print(f"  示例: {stocks[0]['symbol']} - {stocks[0]['name']}")
except:
    print(f"  结果: {result[:200]}...")

# 测试4: tushare数据源（应该不可用）
print("\n4. 测试tushare数据源（应该不可用）:")
result = get_all_china_stocks(source='tushare')
try:
    stocks = json.loads(result)
    print(f"  tushare数据源返回数量: {len(stocks)} (应该是示例数据)")
except:
    print(f"  结果: {result[:200]}...")

# 测试5: sina数据源（应该返回示例数据）
print("\n5. 测试sina数据源（应该返回示例数据）:")
result = get_all_china_stocks(source='sina')
try:
    stocks = json.loads(result)
    print(f"  sina数据源返回数量: {len(stocks)} (应该是示例数据)")
except:
    print(f"  结果: {result[:200]}...")

# 测试6: 直接使用StockDataFetcher
print("\n6. 直接测试StockDataFetcher:")
fetcher = StockDataFetcher()
print(f"  东方财富可用: {fetcher.data_sources['eastmoney'].get('available', False)}")
print(f"  tushare可用: {fetcher.data_sources['tushare'].get('available', False)}")

# 测试7: 测试东方财富数据源获取
print("\n7. 测试东方财富数据源获取:")
try:
    stocks = fetcher._get_eastmoney_stock_list(market='all')
    print(f"  东方财富API返回股票数量: {len(stocks)}")
    if stocks:
        print(f"  前3只: {stocks[0]['symbol']}, {stocks[1]['symbol']}, {stocks[2]['symbol']}")
except Exception as e:
    print(f"  错误: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)