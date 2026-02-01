# AITools Stock Module Documentation

## 📊 Module Overview

AITools Stock Module is a multi-data source financial data acquisition tool that integrates multiple free financial data sources both domestic and international, providing unified API interfaces to obtain stock quotes, company information, and other data.

## 🚀 Core Features

- **Multi-source Support**: Integrates five major data sources: Sina Finance, Tencent Finance, Tushare, yfinance, and pandas-datareader
- **Unified API Interface**: Consistent function calling method, simplifying data acquisition process
- **Automatic Code Conversion**: Supports multiple stock code formats, automatic recognition and standardization
- **Fault Tolerance**: Graceful error handling and fallback mechanisms
- **Flexible Output Format**: Supports both table and JSON output formats

## 📁 File Structure

```
AITools/stock/
├── __init__.py          # Module export file
├── stock.py            # Core implementation code
├── stock.md            # This documentation
├── example_usage.py    # Usage examples
└── stock.py.backup     # Original backup file
```

## 🔧 Installation Dependencies

```bash
# Basic dependencies
pip install tushare yfinance pandas-datareader

# Optional: Set Tushare Token environment variable
export TUSHARE_TOKEN=your_tushare_token
```

## 📊 Completed Work

### 1. **Extended Multi-Source Support**
- **Retained existing data sources**: sina (Sina Finance), tencent (Tencent Finance)
- **New data sources added**:
  - `tushare`: Professional financial data (requires token)
  - `yfinance`: Yahoo Finance global stock data
  - `pandas-datareader`: Multi-source support

### 2. **Unified Data Acquisition Interface**
All data sources use the same function interface, switched via the `source` parameter.

### 3. **Support for Multiple Stock Code Formats**
- A-shares: `sh603060`, `sz000001`, `603060.SS`, `000001.SZ`
- US stocks: `AAPL`, `MSFT`, `GOOGL`
- HK stocks: `0700.HK` (Tencent)
- Automatic recognition and standardization of different formats

### 4. **Core Improvement Features**
- ✅ **Encoding Fix**: Resolved Tencent Finance Chinese garbled text issue
- ✅ **Error Handling**: Graceful fallback mechanism and clear error messages
- ✅ **Auto-detection**: Runtime check of data source availability
- ✅ **Retry Mechanism**: Automatic retry for rate-limited requests
- ✅ **Backward Compatibility**: Fully compatible with existing code

## 🎯 API Reference

### Get Stock Real-time Quotes
```python
get_stock_quote(symbol: str, source: str = 'sina', format: str = 'table') -> str
```
**Parameters:**
- `symbol`: Stock symbol
- `source`: Data source ('sina', 'tencent', 'tushare', 'yfinance', 'pandas-datareader')
- `format`: Output format ('table' or 'json')

**Examples:**
```python
# Sina Finance
get_stock_quote("sh603060", "sina", "table")

# Tencent Finance  
get_stock_quote("sz000001", "tencent", "table")

# Tushare
get_stock_quote("000001.SZ", "tushare", "table")

# Yahoo Finance
get_stock_quote("AAPL", "yfinance", "table")
```

### Get Multiple Stock Quotes in Batch
```python
get_multiple_stock_quotes(symbols: List[str], source: str = 'sina', format: str = 'table') -> str
```

### Search Stock Code
```python
search_stock(query: str, market: str = 'all') -> str
```

### Get Stock Historical K-line Data
```python
get_stock_history(symbol: str, period: str = 'daily', 
                  start_date: str = '', end_date: str = '',
                  count: int = 100) -> str
```

### Get Company Basic Information
```python
get_company_info(symbol: str) -> str
```

## 📈 Data Source Comparison

| Data Source | Advantages | Disadvantages | Use Cases | Example Code |
|-------------|------------|---------------|-----------|--------------|
| **sina** (Sina Finance) | Free, real-time, comprehensive A-share data | Limited to A-shares | A-share real-time quotes | `get_stock_quote("sh603060", "sina")` |
| **tencent** (Tencent Finance) | Free, includes fundamental indicators like PE/PB | Limited to A-shares | A-share fundamental analysis | `get_stock_quote("sz000001", "tencent")` |
| **tushare** | Professional financial data, rich historical data | Requires token, free version has limitations | Quantitative analysis, historical data | `get_stock_quote("000001.SZ", "tushare")` |
| **yfinance** (Yahoo Finance) | Global stock data (US, HK stocks, etc.) | Rate limiting restrictions | US/HK stock quotes | `get_stock_quote("AAPL", "yfinance")` |
| **pandas-datareader** | Multi-source support, commonly used in academic research | Unstable API, complex installation | Academic research, multi-source comparison | `get_stock_quote("AAPL", "pandas-datareader")` |

## 🧪 Usage Examples

Complete examples available in `example_usage.py`:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from stock.stock import get_stock_quote, get_multiple_stock_quotes, search_stock

# Basic usage
print(get_stock_quote("sh603060", "sina", "table"))

# Batch retrieval
print(get_multiple_stock_quotes(["sh603060", "sz000001", "sh600036"], "sina", "table"))

# Stock search
print(search_stock("平安", "all"))

# JSON format output
print(get_stock_quote("sh603060", "sina", "json"))
```

## ⚙️ Environment Configuration

### Tushare Token Configuration
```bash
# Linux/Mac
export TUSHARE_TOKEN=your_tushare_token

# Windows
set TUSHARE_TOKEN=your_tushare_token

# Or set in Python code
import os
os.environ['TUSHARE_TOKEN'] = 'your_tushare_token'
```

### Proxy Configuration (if needed)
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

## ⚠️ Important Notes

1. **Tushare**:
   - Need to register at [tushare.pro](https://tushare.pro) to obtain token
   - Free version has daily call limits
   - Some advanced features require credits

2. **yfinance**:
   - Has request rate limiting
   - May fail when network is unstable
   - Includes retry mechanism, but recommend controlling request frequency

3. **pandas-datareader**:
   - Some data source APIs may be deprecated
   - Requires installation of system dependencies like setuptools
   - Recommended as alternative data source

4. **Network Environment**:
   - Ensure normal network connection
   - Some data sources may require VPN

5. **Data Timeliness**:
   - Real-time data affected by data source update frequency
   - May return previous day's closing price outside trading hours

## 🧪 Test Verification

- ✅ Module import test passed
- ✅ Tool function registration completed
- ✅ Parameter definition validation passed
- ✅ Core function testing completed
- ✅ Example usage code verification passed

---
*Documentation translated from Chinese. Original Chinese version preserved in `stock.md.backup`.*