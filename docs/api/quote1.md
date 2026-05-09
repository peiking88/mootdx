# 标准行情接口

底层基于 `opentdx` 实现，兼容 tdxpy 接口风格。

下面是如何在程序里面调用本接口

**参数说明:**

- market: 对应市场。 (std 标准股票市场，ext 扩展市场)

** 调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
```

### 其他参数

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std', multithread=True, heartbeat=True, bestip=False, timeout=15)
# multithread 多线程
# heartbeat 开启心跳包
# bestip 重新测试最快服务器
# server 自行设置服务器IP, 格式 `server=('127.0.0.1', 7727)`
# timeout 设置超时时间
# quiet 日志静默方式, 默认False, 设置为 True 则不打印日志信息
# verbose 日志显示等级 0, 静默模式, 1 一般级别, 2 详细级别
```

## 01. 查询实时行情

可以获取**多**只股票的行情信息

**参数说明: **

- symbol: 多个股票号码。 `["000001", "600300"]` 格式

返回值：

- pd.DataFrame

**调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.quotes(symbol=["000001", "600300"])
```

## 02. 获取k线数据

**调用方法：**

> frequency -> K线种类
> 0 => 5分钟K线 => 5m
> 1 => 15分钟K线 => 15m
> 2 => 30分钟K线 => 30m
> 3 => 小时K线 => 1h
> 4 => 日K线 (小数点x100) => days
> 5 => 周K线 => week
> 6 => 月K线 => mon
> 7 => 1分钟K线(好像一样) => 1m
> 8 => 1分钟K线(好像一样) => 1m
> 9 => 日K线 => day
> 10 => 季K线 => 3mon
> 11 => 年K线 => year

如

**调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.bars(symbol='600036', frequency=9, offset=10)

# 前复权
client.bars(symbol='600036', adjust='qfq')

# 后复权
client.bars(symbol='600036', adjust='hfq')
```

## 03. 查询股票数量

** 参数说明: **

- market: 市场代码. 0 - 深圳, 1 - 上海 (可以使用常量 `MARKET_SZ`, `MARKET_SH` 代替)

** 调用方法：**

```python
from mootdx.quotes import Quotes
from mootdx import consts

client = Quotes.factory(market='std')
client.stock_count(market=consts.MARKET_SH)
```

## 04. 查询股票列表

** 参数说明: **

- market: 市场代码. 0 - 深圳, 1 - 上海 (可以使用常量 `MARKET_SZ`, `MARKET_SH` 代替)

> 注意，在引入 consts 之后， （`from mootdx import consts`）
> 我们可以使用 consts.MARKET_SH , consts.MARKET_SZ 常量来代替 1 和 0 作为参数

** 调用方法：**

```python
from mootdx.quotes import Quotes
from mootdx import consts

client = Quotes.factory(market='std')
symbol = client.stocks(market=consts.MARKET_SH)
```

## 05. 指数K线行情

** 参数说明: **

- frequency: K线种类
- market: 市场代码. 0 - 深圳, 1 - 上海 (可以使用常量 `MARKET_SZ`, `MARKET_SH` 代替)
- start: 开始位置
- offset: 用户要请求的 K 线数目，最大值为 800

> frequency -> K线种类
> 0 => 5分钟K线 => 5m
> 1 => 15分钟K线 => 15m
> 2 => 30分钟K线 => 30m
> 3 => 小时K线 => 1h
> 4 => 日K线 (小数点x100) => days
> 5 => 周K线 => week
> 6 => 月K线 => mon
> 7 => 1分钟K线(好像一样) => 1m
> 8 => 1分钟K线(好像一样) => 1m
> 9 => 日K线 => day
> 10 => 季K线 => 3mon
> 11 => 年K线 => year

使用说明：

** 调用方法：**

```python
from mootdx.quotes import Quotes
from mootdx.consts import MARKET_SH

client = Quotes.factory(market='std')
client.index(frequency=9, market=MARKET_SH, symbol='000001', start=1, offset=2)
```

## 06. 查询分时行情

> 网友反馈，此接口数据有误，不建议使用，可以使用 后面的 `历史分时行情` 来替代

** 参数说明: **

- symbol: 股票代码

** 调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.minute(symbol='000001')
```

## 07. 历史分时行情

** 参数说明: **

- market: 市场代码.
- symbol: 股票代码
- date: 时间

** 调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.minutes(symbol='000001', date='20171010')
```

注意，在引入 consts 之后， （`from mootdx import consts`） 我们可以使用 consts.MARKET_SH , consts.MARKET_SZ 常量来代替 1 和 0 作为参数

## 08. 查询分笔成交

** 参数说明: **

- market: 市场代码.
- start: 起始位置
- offset: 数量

** 调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.transaction(symbol='600036', start=0, offset=10)
```

## 09. 查询历史分笔

** 参数说明: **

- symbol: 股票代码.
- start: 起始位置.
- offset: 数量.
- date: 日期.

** 调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.transactions(symbol='000001', start=0, offset=10, date='20170209')
```

## 10. 公司信息目录

** 参数说明: **
市场代码， 股票代码， 如： 0,000001 或 1,600300

** 参数说明: **

- symbol: 股票代码.

** 调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.F10C(symbol='000001')
```

## 11. 公司信息详情

** 参数说明: **

- symbol: 股票代码.
- name: 公司详情标题. 可使用`F10C`获取

**调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.F10(symbol='000001', name='最新提示')
```

注意这里的 公司详情标题 参考上面接口的返回结果。

## 12. 除权除息信息

**参数说明: **

- symbol: 股票代码.

** 调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.xdxr(symbol='600036')
```

## 13. 读取财务信息

**参数说明: **

- symbol: 股票代码.

**调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.finance(symbol="600300")
```

## 14. 读取 OHLC k线信息

**参数说明: **

- symbol: 股票代码.
- begin: 开始时间.
- end: 结束时间.
- adjust: 复权.

**调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.k(symbol="600300", begin="2017-07-03", end="2017-07-10")

# 前复权
client.k(symbol="600300", begin="2017-07-03", end="2017-07-10", adjust='qfq')

# 后复权
client.k(symbol="600300", begin="2017-07-03", end="2017-07-10", adjust='hfq')

# ohlc 是k的别名, 功能相同
client.ohlc(symbol="600300", begin="2017-07-03", end="2017-07-10")

# 前复权
client.ohlc(symbol="600300", begin="2017-07-03", end="2017-07-10", adjust='qfq')

# 后复权
client.ohlc(symbol="600300", begin="2017-07-03", end="2017-07-10", adjust='hfq')
```

## 15. 板块列表

获取行业、概念、地域等板块分类

**参数说明:**

- board_type: 板块类型。`industry` 行业, `concept` 概念, `style` 风格, `region` 地区, `all` 全部
- count: 获取数量，默认 10000

**调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')

# 获取行业板块
client.board_list(board_type='industry')

# 获取概念板块
client.board_list(board_type='concept')
```

## 16. 板块成分股行情

获取指定板块的成分股行情数据

**参数说明:**

- board_symbol: 板块代码，如 `880001`
- count: 获取数量，默认 20
- sort_type: 排序字段，默认按涨跌幅
- sort_order: 排序方向，默认降序

**调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.board_quotes('880001', count=20)
```

## 17. 个股资金流向

**参数说明:**

- symbol: 股票代码

**调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.capital_flow('000001')
```

## 18. 排行榜

获取涨停、跌停、振幅、涨速等排行榜

**参数说明:**

- category: 排行类别（opentdx CATEGORY 枚举），默认全部A股

**调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.stock_ranking()
```

## 19. 排序筛选股票列表

**参数说明:**

- category: 股票类别，默认全部A股
- sort_type: 排序字段，默认涨跌幅
- count: 获取数量，默认 80
- filter_types: 筛选类型列表

**调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.stock_list_sorted(count=80)
```

## 20. 集合竞价

**参数说明:**

- symbol: 股票代码

**调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.auction('000001')
```

## 21. 异动预警

**参数说明:**

- market: 市场代码，0 深市, 1 沪市

**调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.unusual(market=0)
```

## 22. 成交分布

**参数说明:**

- symbol: 股票代码

**调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.vol_profile('000001')
```

## 23. 指数行情

批量获取指数行情

**参数说明:**

- symbol_list: 指数代码列表，如 `['000001', '399001']`

**调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.index_info(['000001', '399001'])
```

## 24. 全市场股票列表

一次获取沪深两市所有股票

**调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.stock_all()
```

## 25. 板块文件数据

获取证券板块文件数据

**参数说明:**

- tofile: 板块文件名，如 `block.dat`

**调用方法：**

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')
client.block(tofile='block_zs.dat')
```
