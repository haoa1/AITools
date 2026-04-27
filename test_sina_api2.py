#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
import requests

print('Testing sina stock list with different parameters...')

# Try different nodes
nodes = ['hs_a', 'sh_a', 'sz_a', 'sh_b', 'sz_b']
for node in nodes:
    try:
        url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData'
        params = {
            'page': 1,
            'num': 5,
            'sort': 'symbol',
            'asc': 1,
            'node': node
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://finance.sina.com.cn',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        print(f'\nNode: {node}, Status: {resp.status_code}')
        print('Content type:', resp.headers.get('content-type'))
        if resp.status_code == 200:
            text = resp.text
            if len(text) < 500:
                print('Response:', text)
            else:
                print('First 500 chars:', text[:500])
    except Exception as e:
        print(f'Error for node {node}: {e}')