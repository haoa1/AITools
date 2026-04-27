#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from stock.stock import get_all_china_stocks
import json

# Test with default parameters
result = get_all_china_stocks()
print('Total stocks returned:', len(result))
print('First 5 stocks:')
for stock in result[:5]:
    print(f"  {stock['symbol']}: {stock['name']}")

# Test with market='sh'
result_sh = get_all_china_stocks(market='sh')
print('\nSH stocks count:', len(result_sh))

# Test with market='sz'
result_sz = get_all_china_stocks(market='sz')
print('SZ stocks count:', len(result_sz))

# Test with source='sina'
result_sina = get_all_china_stocks(source='sina')
print('\nSina source stocks count:', len(result_sina))

# Test with source='tencent'
result_tencent = get_all_china_stocks(source='tencent')
print('Tencent source stocks count:', len(result_tencent))