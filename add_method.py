#!/usr/bin/env python3
import sys

with open('stock/stock.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到 search_stock 方法的结束位置
end_line = -1
start_line = -1
for i, line in enumerate(lines):
    if 'return filtered_results if filtered_results else example_results[:3]' in line:
        end_line = i
        # 找到下一个方法开始
        for j in range(i+1, len(lines)):
            if lines[j].strip().startswith('def get_stock_history'):
                start_line = j
                break
        break

if start_line == -1:
    print("未找到 get_stock_history 方法")
    sys.exit(1)

# 新方法文本
new_method = '''    def get_all_china_stocks(self, market: str = 'all', source: str = 'tushare') -> List[Dict[str, Any]]:
        \\"\\"\\"获取所有中国股票列表
        
        Args:
            market: 市场，'sh'（上海），'sz'（深圳），'all'（全部）
            source: 数据源，'tushare'（默认），'sina'，'tencent'
            
        Returns:
            股票列表，每个股票包含 symbol, name, code, market, type 等字段
        \\"\\"\\"
        # 如果数据源是tushare且可用，尝试使用tushare
        if source.lower() == 'tushare' and self.data_sources['tushare'].get('available', False):
            try:
                import tushare as ts
                # 检查是否有token
                has_token = self.data_sources['tushare'].get('has_token', True)
                if has_token:
                    pro = ts.pro_api()
                    # 获取所有股票基本信息
                    df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
                else:
                    # 使用旧接口
                    df = ts.get_stock_basics()
                
                # 转换为字典列表
                stocks = []
                for _, row in df.iterrows():
                    ts_code = row['ts_code'] if 'ts_code' in row else row['code']
                    symbol = self._normalize_symbol(ts_code, 'sina')
                    # 根据市场代码过滤
                    if market == 'all' or (market == 'sh' and symbol.startswith('sh')) or (market == 'sz' and symbol.startswith('sz')):
                        stocks.append({
                            'symbol': symbol,
                            'name': row['name'] if 'name' in row else '',
                            'code': ts_code,
                            'market': 'SH' if symbol.startswith('sh') else 'SZ',
                            'type': 'stock',
                            'area': row.get('area', ''),
                            'industry': row.get('industry', ''),
                            'list_date': row.get('list_date', '')
                        })
                return stocks
            except Exception as e:
                # 如果tushare失败，回退到示例数据
                pass
        
        # 示例数据
        example_stocks = [
            {
                'symbol': 'sh603060',
                'name': '国检集团',
                'code': '603060',
                'market': 'SH',
                'type': 'stock'
            },
            {
                'symbol': 'sz000001',
                'name': '平安银行',
                'code': '000001',
                'market': 'SZ',
                'type': 'stock'
            },
            {
                'symbol': 'sh600036',
                'name': '招商银行',
                'code': '600036',
                'market': 'SH',
                'type': 'stock'
            },
            {
                'symbol': 'sh600519',
                'name': '贵州茅台',
                'code': '600519',
                'market': 'SH',
                'type': 'stock'
            },
            {
                'symbol': 'sz000858',
                'name': '五粮液',
                'code': '000858',
                'market': 'SZ',
                'type': 'stock'
            }
        ]
        
        # 根据市场过滤示例数据
        filtered = []
        for stock in example_stocks:
            if market == 'all' or (market == 'sh' and stock['market'] == 'SH') or (market == 'sz' and stock['market'] == 'SZ'):
                filtered.append(stock)
        return filtered
'''

# 在 start_line 之前插入新方法
lines.insert(start_line, new_method + '\\n')

with open('stock/stock.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('插入成功')