#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
import stock.stock as stock_module

print("测试当前状态...")

# 创建fetcher实例
fetcher = stock_module.StockDataFetcher()

# 检查数据源状态
print("数据源状态:")
for source, info in fetcher.data_sources.items():
    print(f"  {source}: {info.get('available', False)}")

# 测试get_all_china_stocks，但设置非常短的超时
print("\n测试get_all_china_stocks...")

# 临时修改方法以避免网络超时
original_method = fetcher._get_eastmoney_stock_list
fetcher._get_eastmoney_stock_list = lambda market='all', max_pages=1: []

try:
    stocks = fetcher.get_all_china_stocks()
    print(f"获取到 {len(stocks)} 只股票")
    
    # 检查返回的数据
    if stocks:
        print(f"前5只股票:")
        for i, stock in enumerate(stocks[:5]):
            print(f"  {stock['symbol']} - {stock['name']}")
        
        print(f"\n市场分布:")
        sh_count = sum(1 for s in stocks if s['market'] == 'SH')
        sz_count = sum(1 for s in stocks if s['market'] == 'SZ')
        print(f"  上海: {sh_count} 只")
        print(f"  深圳: {sz_count} 只")
finally:
    # 恢复原始方法
    fetcher._get_eastmoney_stock_list = original_method