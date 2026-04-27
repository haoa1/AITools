#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from stock.stock import StockDataFetcher
import requests

fetcher = StockDataFetcher()
print('Testing sina stock list...')
try:
    # Try to get sina stock list
    url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData'
    params = {
        'page': 1,
        'num': 10,
        'sort': 'symbol',
        'asc': 1,
        'node': 'hs_a'
    }
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    print('Status:', resp.status_code)
    print('Content type:', resp.headers.get('content-type'))
    print('First 500 chars:', resp.text[:500])
except Exception as e:
    print('Error:', e)