#!/usr/bin/env python
"""
AITools Stock Module Usage Example

This module supports multiple data sources:
1. sina - Sina Finance (default, A-share data)
2. tencent - Tencent Finance (A-share data)
3. tushare - Tushare (requires token, A-share data)
4. yfinance - Yahoo Finance (global stock data)
5. pandas-datareader - Pandas DataReader (multiple data sources)

Before using, ensure required libraries are installed:
pip install tushare yfinance pandas-datareader

For tushare, it's recommended to set TUSHARE_TOKEN environment variable for more features:
export TUSHARE_TOKEN=your_tushare_token
export TUSHARE_TOKEN=your_tushare_token
"""

import sys
import os

# Add AITools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from stock.stock import (
    get_stock_quote,
    get_multiple_stock_quotes,
    search_stock,
    get_stock_history,
    get_company_info
)

def example_basic_usage():
    """基本使用示例"""
    print("=" * 60)
    print("AITools股票模块 - 基本使用示例")
    print("=" * 60)
    
    # 示例1: 获取单只股票行情（新浪财经）
    print("\n1. 获取单只股票行情（新浪财经）:")
    result = get_stock_quote("sh603060", "sina", "table")
    print(result)
    
    # 示例2: 获取单只股票行情（腾讯财经）
    print("\n2. 获取单只股票行情（腾讯财经）:")
    result = get_stock_quote("sz000001", "tencent", "table")
    print(result)
    
    # 示例3: 获取美股行情（yfinance）
    print("\n3. 获取美股行情（yfinance）:")
    try:
        result = get_stock_quote("AAPL", "yfinance", "table")
        print(result)
    except Exception as e:
        print(f"注意: {e}")
        print("yfinance可能受到请求限制，请稍后重试")
    
    # 示例4: 批量获取股票行情
    print("\n4. 批量获取股票行情:")
    result = get_multiple_stock_quotes(["sh603060", "sz000001", "sh600036"], "sina", "table")
    print(result)
    
    # 示例5: 搜索股票
    print("\n5. 搜索股票:")
    result = search_stock("平安", "all")
    print(result)
    
    # 示例6: JSON格式输出
    print("\n6. JSON格式输出:")
    result = get_stock_quote("sh603060", "sina", "json")
    print(result[:200] + "..." if len(result) > 200 else result)

def example_advanced_usage():
    """高级使用示例"""
    print("\n" + "=" * 60)
    print("AITools股票模块 - 高级使用示例")
    print("=" * 60)
    
    # 不同数据源对比
    print("\n1. 不同数据源对比:")
    symbols = ["sh603060", "AAPL", "000001.SZ"]
    
    for symbol in symbols:
        print(f"\n股票: {symbol}")
        print("-" * 40)
        
        # 尝试不同数据源
        for source in ["sina", "tencent", "tushare", "yfinance"]:
            try:
                if symbol.startswith("sh") or symbol.startswith("sz") or ".S" in symbol:
                    # A股
                    if source in ["sina", "tencent", "tushare"]:
                        result = get_stock_quote(symbol, source, "table")
                        lines = result.split('\n')
                        price_line = lines[1] if len(lines) > 1 else "N/A"
                        print(f"  {source:15}: {price_line}")
                else:
                    # 美股
                    if source == "yfinance":
                        result = get_stock_quote(symbol, source, "table")
                        lines = result.split('\n')
                        price_line = lines[1] if len(lines) > 1 else "N/A"
                        print(f"  {source:15}: {price_line}")
            except Exception as e:
                print(f"  {source:15}: 错误 - {str(e)[:50]}")

def example_data_source_selection():
    """数据源选择指南"""
    print("\n" + "=" * 60)
    print("数据源选择指南")
    print("=" * 60)
    
    print("""
根据需求选择数据源：

1. 新浪财经 (sina):
   - 优点: 免费、实时、A股数据全面
   - 缺点: 仅限A股
   - 示例: get_stock_quote("sh603060", "sina")

2. 腾讯财经 (tencent):
   - 优点: 免费、实时、A股数据带有PE/PB等指标
   - 缺点: 仅限A股
   - 示例: get_stock_quote("sz000001", "tencent")

3. Tushare (tushare):
   - 优点: 专业金融数据，历史数据丰富
   - 缺点: 需要token，免费版有限制
   - 设置: export TUSHARE_TOKEN=你的token
   - 示例: get_stock_quote("000001.SZ", "tushare")

4. Yahoo Finance (yfinance):
   - 优点: 全球股票数据，包括美股、港股等
   - 缺点: 有请求限制，不稳定
   - 示例: get_stock_quote("AAPL", "yfinance")

5. Pandas DataReader (pandas-datareader):
   - 优点: 多数据源支持
   - 缺点: 安装复杂，API经常变化
   - 示例: get_stock_quote("AAPL", "pandas-datareader")

股票代码格式:
- A股: sh603060, sz000001, 603060.SS, 000001.SZ
- 美股: AAPL, MSFT, GOOGL
- 港股: 0700.HK (腾讯)
""")

def example_environment_setup():
    """环境设置示例"""
    print("\n" + "=" * 60)
    print("环境设置示例")
    print("=" * 60)
    
    print("""
1. 安装所需库:
   pip install tushare yfinance pandas-datareader

2. 设置TUSHARE_TOKEN环境变量（可选）:
   Linux/Mac: export TUSHARE_TOKEN=你的tushare_token
   Windows: set TUSHARE_TOKEN=你的tushare_token

3. 或者在代码中设置:
   import os
   os.environ['TUSHARE_TOKEN'] = '你的tushare_token'

4. 使用代理（如果需要）:
   export HTTP_PROXY=http://proxy.example.com:8080
   export HTTPS_PROXY=http://proxy.example.com:8080
""")

if __name__ == "__main__":
    example_basic_usage()
    example_advanced_usage()
    example_data_source_selection()
    example_environment_setup()
    
    print("\n" + "=" * 60)
    print("示例完成！更多功能请查看stock.py源代码。")
    print("=" * 60)