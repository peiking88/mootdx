# 市场
MARKET_SZ = 0  # 深市
MARKET_SH = 1  # 沪市
MARKET_BJ = 2  # 北交

# K线种类
# 0 -   5 分钟K 线
KLINE_5MIN = 0
# 1 -   15 分钟K 线
KLINE_15MIN = 1
# 2 -   30 分钟K 线
KLINE_30MIN = 2
# 3 -   1 小时K 线
KLINE_1HOUR = 3
# 4 -   日K 线
KLINE_DAILY = 4
# 5 -   周K 线
KLINE_WEEKLY = 5
# 6 -   月K 线
KLINE_MONTHLY = 6
# 7 -   扩展市场 1 分钟
KLINE_EX_1MIN = 7
# 8 -   1 分钟K 线
KLINE_1MIN = 8
# 9 -   日K 线
KLINE_RI_K = 9
# 10 -  季K 线
KLINE_3MONTH = 10
# 11 -  年K 线
KLINE_YEARLY = 11

# 分笔行情最多2000条
MAX_TRANSACTION_COUNT = 2000

# K线数据最多800条
MAX_KLINE_COUNT = 800

# 板块相关参数
BLOCK_SZ = 'block_zs.dat'
BLOCK_FG = 'block_fg.dat'
BLOCK_GN = 'block_gn.dat'
BLOCK_DEFAULT = 'block.dat'

TYPE_FLATS = 0
TYPE_GROUP = 1

# 服务器列表统一从 opentdx 动态获取，避免硬编码过期
from opentdx.const import main_hosts as _main_hosts
from opentdx.const import ex_hosts as _ex_hosts

HQ_HOSTS = list(_main_hosts)
EX_HOSTS = list(_ex_hosts)

GP_HOSTS = [
    ('默认财务数据线路', '120.76.152.87', 7709),
]

HF_HOSTS = [
    ('上海双线高级行情1', '121.37.183.82', 7709),
    ('深圳双线高级行情1', '110.41.174.169', 7709),
]

def return_last_value(retry_state):
    """return the result of the last call attempt"""
    return retry_state.outcome.result()
