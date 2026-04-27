#!/usr/bin/env python3
import requests
import json
import time

def test_eastmoney_api():
    """测试东方财富API"""
    print("=" * 60)
    print("测试东方财富股票列表API")
    print("=" * 60)
    
    # 东方财富股票列表API
    # 上海A股列表
    urls_to_test = [
        {
            'name': '东方财富-上海A股',
            'url': 'http://push2.eastmoney.com/api/qt/clist/get',
            'params': {
                'pn': 1,
                'pz': 20,
                'po': 1,
                'np': 1,
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fltt': 2,
                'invt': 2,
                'fid': 'f3',
                'fs': 'm:1+t:2,m:1+t:23',
                'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152',
                '_': str(int(time.time() * 1000))
            }
        },
        {
            'name': '东方财富-深圳A股',
            'url': 'http://push2.eastmoney.com/api/qt/clist/get',
            'params': {
                'pn': 1,
                'pz': 20,
                'po': 1,
                'np': 1,
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fltt': 2,
                'invt': 2,
                'fid': 'f3',
                'fs': 'm:0+t:6,m:0+t:80',
                'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152',
                '_': str(int(time.time() * 1000))
            }
        },
        {
            'name': '东方财富-全部A股',
            'url': 'http://push2.eastmoney.com/api/qt/clist/get',
            'params': {
                'pn': 1,
                'pz': 20,
                'po': 1,
                'np': 1,
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fltt': 2,
                'invt': 2,
                'fid': 'f3',
                'fs': 'm:0+t:6,m:1+t:2,m:0+t:80,m:1+t:23',
                'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152',
                '_': str(int(time.time() * 1000))
            }
        }
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'http://quote.eastmoney.com/center/gridlist.html',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    for test in urls_to_test:
        print(f"\n测试: {test['name']}")
        print("-" * 40)
        try:
            response = requests.get(test['url'], params=test['params'], headers=headers, timeout=10)
            print(f"状态码: {response.status_code}")
            print(f"内容类型: {response.headers.get('content-type')}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"响应格式: JSON (keys: {list(data.keys()) if isinstance(data, dict) else 'not dict'})")
                    
                    if 'data' in data and 'diff' in data['data']:
                        stocks = data['data']['diff']
                        print(f"股票数量: {len(stocks)}")
                        if stocks:
                            first_stock = stocks[0]
                            print(f"示例股票: {first_stock.get('f12', 'N/A')} - {first_stock.get('f14', 'N/A')}")
                    else:
                        print("响应内容 (前500字符):")
                        print(response.text[:500])
                except json.JSONDecodeError:
                    print("响应不是JSON格式")
                    print("响应内容 (前500字符):")
                    print(response.text[:500])
            else:
                print(f"错误: HTTP {response.status_code}")
        except Exception as e:
            print(f"请求失败: {e}")
        
        time.sleep(1)  # 避免请求过快

def test_tushare_availability():
    """测试tushare可用性"""
    print("\n" + "=" * 60)
    print("测试tushare可用性")
    print("=" * 60)
    
    try:
        import tushare as ts
        print("tushare已安装")
        
        # 检查是否有token
        token = ts.get_token()
        if token:
            print(f"tushare token: {token[:10]}...")
            # 测试获取数据
            try:
                pro = ts.pro_api()
                # 尝试获取少量数据测试
                df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name', limit=5)
                print("tushare接口可用，示例数据:")
                print(df)
                return True
            except Exception as e:
                print(f"tushare接口测试失败: {e}")
                return False
        else:
            print("tushare token未设置")
            # 测试旧接口
            try:
                df = ts.get_stock_basics()
                print("tushare旧接口可用，数据形状:", df.shape)
                return True
            except Exception as e:
                print(f"tushare旧接口测试失败: {e}")
                return False
    except ImportError:
        print("tushare未安装")
        return False

if __name__ == "__main__":
    test_eastmoney_api()
    test_tushare_availability()