# 通达信数据读取接口

[![image](https://badge.fury.io/py/mootdx.svg)](http://badge.fury.io/py/mootdx)
[![image](https://img.shields.io/travis/bopo/mootdx.svg)](https://travis-ci.org/mootdx/mootdx)
[![Documentation Status](https://readthedocs.org/projects/mootdx/badge/?version=latest)](https://mootdx.readthedocs.io/zh/latest/?badge=latest)
[![Updates](https://pyup.io/repos/github/mootdx/mootdx/shield.svg)](https://pyup.io/repos/github/mootdx/mootdx/)

如果喜欢本项目可以在右上角给颗⭐！你的支持是我最大的动力😎！

**郑重声明: 本项目只作学习交流, 不得用于任何商业目的.**

- 开源协议: MIT license
- 在线文档: <https://www.mootdx.com>
- 国内镜像: <https://gitee.com/ibopo/mootdx>
- 项目仓库: <https://github.com/mootdx/mootdx>
- 问题交流: <https://github.com/mootdx/mootdx/issues>

## 版本更新(倒序)

- 0.11.7: 新增行情适配器层，支持 opentdx 新协议；更新全部行情服务器地址；新增 HF 高级行情支持；修复 pandas 兼容性问题；测试覆盖率提升至 80%

版本更新日志: <https://mootdx.readthedocs.io/zh_CN/latest/history/>

## 运行环境

- 操作系统: Windows / MacOS / Linux 都可以运行.
- Python: 3.8 以及以上版本.

## 安装方法

> 新手建议使用 `pip install -U 'mootdx[all]'` 安装

### PIP 安装方法

```shell

# 包含核心依赖安装
pip install 'mootdx'

# 包含命令行依赖安装, 如果使用命令行工具可以使用这种方式安装
pip install 'mootdx[cli]'

# 包含所有扩展依赖安装, 如果不清楚各种依赖关系就用这个命令
pip install 'mootdx[all]'
```

### 升级安装

```shell
pip install -U opentdx mootdx
```

> 如果不清楚各种依赖关系就用这个命令 `pip install -U 'mootdx[all]'`

## 使用说明

> 以下只列举一些例子, 详细说明请查看在线文档: <https://www.mootdx.com>

通达信离线数据读取

```python
from mootdx.reader import Reader

# market 参数 std 为标准市场(就是股票), ext 为扩展市场(期货，黄金等)
# tdxdir 是通达信的数据目录, 根据自己的情况修改

reader = Reader.factory(market='std', tdxdir='C:/new_tdx')

# 读取日线数据
reader.daily(symbol='600036')

# 读取分钟数据
reader.minute(symbol='600036')

# 读取时间线数据
reader.fzline(symbol='600036')
```

通达信线上行情读取

```python
from mootdx.quotes import Quotes

# 标准市场
client = Quotes.factory(market='std', multithread=True, heartbeat=True)

# k 线数据
client.bars(symbol='600036', frequency=9, offset=10)

# 指数
client.index(symbol='000001', frequency=9)

# 分钟
client.minute(symbol='000001')
```

通达信财务数据读取

```python
from mootdx.affair import Affair

# 远程文件列表
files = Affair.files()

# 下载单个
Affair.fetch(downdir='tmp', filename='gpcw19960630.zip')

# 下载全部
Affair.parse(downdir='tmp')
```

## 加微信交流

![](docs/img/IMG_2851.JPG)

## 常见问题

M1 mac 系统PyMiniRacer不能使用，访问:
<https://github.com/sqreen/PyMiniRacer/issues/143>

## Stargazers over time

[![Stargazers over time](https://starchart.cc/mootdx/mootdx.svg)](https://starchart.cc/mootdx/mootdx)

### 2026-05-04 10:51:50

```
 .gitignore                       |   3 +
 CLAUDE.md                        |  29 +++
 README.md                        |   2 +
 mootdx/config.py                 |   7 +
 mootdx/consts.py                 | 110 ++++++-----
 mootdx/exhq_adapter.py           | 293 ++++++++++++++++++++++++++++
 mootdx/financial/base.py         |   2 +-
 mootdx/financial/financial.py    |   6 +-
 mootdx/hq_adapter.py             | 398 +++++++++++++++++++++++++++++++++++++++
 mootdx/quotes.py                 | 231 +++++++++++++++++++++--
 mootdx/server.py                 |  16 +-
 mootdx/tdxfinder.py              |  76 ++++++++
 mootdx/tools/reversion.py        |   5 +-
 mootdx/utils/__init__.py         |   6 +-
 summary.md                       |  27 +++
```

### 2026-05-04 18:08:00

```
 README.md                    |   2 +-
 summary.md                   |  32 ++++--
 tests/test_adapter_tdxpy.py  | 225 +++++++++++++++++++++++++++++++++++++++++++
 tests/test_affair_unit.py    | 111 +++++++++++++++++++++
 tests/test_config.py         |  75 +++++++++++++++
 tests/test_config_setup.py   |  63 ++++++++++++
 tests/test_exceptions.py     |  61 ++++++++++++
 tests/test_exhq_adapter.py   |  90 +++++++++++++++++
 tests/test_hq_adapter.py     | 180 ++++++++++++++++++++++++++++++++++
 tests/test_quotes_more.py    | 157 ++++++++++++++++++++++++++++++
 tests/test_quotes_opentdx.py | 147 ++++++++++++++++++++++++++++
 tests/test_quotes_unit.py    | 111 +++++++++++++++++++++
 tests/test_server_more.py    |  70 ++++++++++++++
 tests/test_server_unit.py    |  66 +++++++++++++
 tests/test_tdxfinder.py      | 167 ++++++++++++++++++++++++++++++++
```

### 2026-05-09 09:06:08
```
 README.md                    |  41 ++--
 docs/api/quote1.md           | 235 +++++++++++++++++--
 docs/api/quote2.md           |   2 +-
 docs/index.md                |   4 +-
 mootdx/__init__.py           |   2 +-
 mootdx/contrib/compat.py     |  95 +-------
 mootdx/exhq_adapter.py       | 352 +++++++++++++---------------
 mootdx/hq_adapter.py         | 534 +++++++++++++++++++------------------------
 mootdx/parse.py              |   2 +-
 mootdx/reader.py             |   6 +-
 mootdx/tools/customize.py    |   2 +-
 pyproject.toml               |   5 +-
 requirements.txt             |   2 +-
 summary.md                   |  41 +++-
 tests/test_adapter_tdxpy.py  | 239 ++++++++++++-------
```

### 2026-05-09 12:19:42
```
 {sample => scripts/examples}/basic_adjust.py      | 0
 {sample => scripts/examples}/basic_affairs.py     | 0
 {sample => scripts/examples}/basic_quotes.py      | 0
 {sample => scripts/examples}/basic_reader.py      | 0
 {sample => scripts/examples}/fq.py                | 0
 {sample => scripts/examples}/fuquan.py            | 0
 {sample => scripts/examples}/lru_cache.py         | 0
 {sample => scripts/examples}/parse_affairs_all.py | 0
 {sample => scripts/examples}/verify_server.py     | 0
 9 files changed, 0 insertions(+), 0 deletions(-)
```

### 2026-05-09 12:21:55
```
 .coveragerc                                       |   0
 .drone.yml                                        |   2 +-
 .github/workflows/django.yml                      |   0
 .pre-commit-config.yaml                           |  38 +-
 .readthedocs.yaml                                 |   4 +-
 CLAUDE.md                                         |   9 +-
 Dockerfile                                        |   0
 Makefile                                          |   3 -
 README.md                                         |  33 ++
 docs/api/extras.md                                |   2 +-
 docs/faq/py_mini_racer.md                         |   0
 docs/history.md                                   | 140 +++---
 docs/img/todo.md                                  |   7 +-
 docs/setup.md                                     |   1 -
 docs/todo.md                                      |   3 +-
```

### 2026-05-09 12:50:27
```
 mootdx/__init__.py           |   2 +-
 mootdx/config.py             |   0
 mootdx/consts.py             | 115 +++++++--
 mootdx/exceptions.py         |   0
 mootdx/logger.py             |   0
 mootdx/server.py             |   6 +-
 mootdx/utils/__init__.py     |   0
 mootdx/utils/adjust.py       |   0
 mootdx/utils/demjson.py      |   0
 mootdx/utils/factor.py       |   0
 mootdx/utils/holiday.js      | 568 +++++++++++++++++++------------------------
 mootdx/utils/holiday.py      |   0
 mootdx/utils/pandas_cache.py |   0
 mootdx/utils/timer.py        |   0
 mootdx/version.py            |   0
```

### 2026-05-09 18:57:03
```
 mootdx/__init__.py        |   2 +-
 mootdx/config.py          |  14 +------
 mootdx/quotes.py          |  13 ++++--
 mootdx/server.py          |   4 --
 mootdx/utils/__init__.py  | 105 ----------------------------------------------
 summary.md                |  40 ++++--------------
 tests/test_config.py      |   8 +---
 tests/test_server_more.py |   6 +--
 tests/test_server_unit.py |   7 +---
 9 files changed, 22 insertions(+), 177 deletions(-)
```

### 2026-05-10 01:20:00
```
 mootdx/__init__.py                                 |   2 +-
 mootdx/__main__.py                                 |   3 +-
 mootdx/logger.py                                   |  24 +++-
 mootdx/quotes.py                                   |  41 +++---
 mootdx/server.py                                   |   5 +-
 mootdx/tools/customize.py                          |   4 +
 mootdx/tools/reversion.py                          |   4 +-
 mootdx/utils/factor.py                             |  85 ++++++-----
 pyproject.toml                                     |   2 +-
 summary.md                                         |  46 ++++--
 tests/conftest.py                                  |  17 +++
 tests/quotes/test_quotes_base.py                   |   4 +
 tests/quotes/test_quotes_ext.py                    |   8 +-
 tests/quotes/test_quotes_std.py                    |  16 ++-
 ...st_adapter_tdxpy.py => test_adapter_opentdx.py} |   2 +-
```
