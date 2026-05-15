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

- 1.0.0: 同步项目版本号，发布 1.0.0 稳定版本
- 0.15.5: 服务器列表从 opentdx 动态获取；修复网络检测过期导致测试跳过；完善深圳创业板/指数市场识别
- 0.15.4: 库化日志配置、移除死代码、增强复权因子获取
- 0.15.3: 消除重复代码、修复 `__all__` 不匹配、内联薄包装、命名魔数
- 0.15.2: 清理异常使用、删除死代码
- 0.14.0: 增强功能并下沉通用能力到 opentdx
- 0.13.0: 迁移至 opentdx 纯依赖
- 0.11.7: 新增行情适配器层，支持 opentdx 新协议；更新全部行情服务器地址；新增 HF 高级行情支持；修复 pandas 兼容性问题；测试覆盖率提升至 80%

版本更新日志: <https://mootdx.readthedocs.io/zh_CN/latest/history/>

## 运行环境

- 操作系统: Windows / MacOS / Linux
- Python: 3.8 以及以上版本

## 安装方法

> 新手建议使用 `pip install -U 'mootdx[all]'` 安装

### PIP 安装方法

```shell
# 包含核心依赖安装
pip install 'mootdx'

# 包含命令行依赖安装
pip install 'mootdx[cli]'

# 包含所有扩展依赖安装
pip install 'mootdx[all]'
```

### 升级安装

```shell
pip install -U opentdx mootdx
```

> 如果不清楚各种依赖关系就用这个命令 `pip install -U 'mootdx[all]'`

## 使用说明

> 以下只列举一些例子, 详细说明请查看在线文档: <https://www.mootdx.com>

### 通达信离线数据读取

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

### 通达信线上行情读取

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

### 通达信财务数据读取

```python
from mootdx.affair import Affair

# 远程文件列表
files = Affair.files()

# 下载单个
Affair.fetch(downdir='tmp', filename='gpcw19960630.zip')

# 下载全部
Affair.parse(downdir='tmp')
```

## 项目结构

```
mootdx/
├── quotes.py          # 在线行情接口（标准/扩展市场）
├── hq_adapter.py      # 标准行情适配器（封装 opentdx）
├── exhq_adapter.py    # 扩展行情适配器
├── reader.py          # 本地数据读取器
├── affair.py          # 财务文件下载与解析
├── server.py          # 服务器测速与最优 IP 选择
├── config.py          # 全局配置管理
├── consts.py          # 常量定义（市场代码、频率等）
├── parse.py           # 板块数据解析
├── tdxfinder.py       # 通达信安装目录自动查找
├── contrib/           # 扩展功能（复权计算、兼容层）
├── financial/         # 财务数据处理
├── tools/             # 工具集（下载、格式转换等）
└── utils/             # 工具函数（复权、因子、节假日）
```

## 常见问题

M1 mac 系统PyMiniRacer不能使用，访问:
<https://github.com/sqreen/PyMiniRacer/issues/143>

## 加微信交流

![](docs/img/IMG_2851.JPG)

## Stargazers over time

[![Stargazers over time](https://starchart.cc/mootdx/mootdx.svg)](https://starchart.cc/mootdx/mootdx)

### 2026-05-13 14:38:36
```
 mootdx/__init__.py        |  2 +-
 pyproject.toml            |  2 +-
 summary.md                | 16 ++++----
 tests/test_quotes_more.py | 94 ++++++++++++++++++++++++++++++++++-------------
 tests/test_useless.py     | 41 ---------------------
 5 files changed, 80 insertions(+), 75 deletions(-)
```
