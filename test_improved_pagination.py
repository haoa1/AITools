#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from stock.stock import StockDataFetcher

print("=" * 60)
print("测试改进的分页功能")
print("=" * 60)

fetcher = StockDataFetcher()

# 测试获取前几页（减少页数以加快测试）
print("\n1. 测试获取前3页股票（所有市场）:")
stocks = fetcher._get_eastmoney_stock_list(market='all', max_pages=3)
print(f"总股票数量: {len(stocks)}")

# 统计市场分布
if stocks:
    sh_count = sum(1 for s in stocks if s['market'] == 'SH')
    sz_count = sum(1 for s in stocks if s['market'] == 'SZ')
    print(f"上海市场: {sh_count} 只")
    print(f"深圳市场: {sz_count} 只")
    
    print(f"\n前10只股票:")
    for i, stock in enumerate(stocks[:10]):
        print(f"  {i+1:2d}. {stock['symbol']} - {stock['name']}")

# 测试通过get_all_china_stocks获取
print("\n2. 测试通过get_all_china_stocks获取（前2页）:")
# 临时修改方法以限制页数
import stock.stock as stock_module
original_method = stock_module.StockDataFetcher._get_eastmoney_stock_list

def limited_method(self, market='all', max_pages=2):
    return original_method(self, market, max_pages)

stock_module.StockDataFetcher._get_eastmoney_stock_list = limited_method

all_stocks = fetcher.get_all_china_stocks()
print(f"获取到 {len(all_stocks)} 只股票")

# 恢复原始方法
stock_module.StockDataFetcher._get_eastmoney_stock_list = original_method

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)