"""常量定义，统一从 opentdx 导入服务器列表和市场/周期枚举"""
from opentdx.const import main_hosts as HQ_HOSTS
from opentdx.const import ex_hosts as EX_HOSTS
from opentdx.const import MARKET
from opentdx.const import PERIOD

# 市场代码（从 MARKET 枚举派生，保持整数向后兼容）
MARKET_SZ = MARKET.SZ.value  # 0
MARKET_SH = MARKET.SH.value  # 1
MARKET_BJ = MARKET.BJ.value  # 2

# K线周期（从 PERIOD 枚举派生，保持整数向后兼容）
KLINE_5MIN = PERIOD.MIN_5.value       # 0
KLINE_15MIN = PERIOD.MIN_15.value     # 1
KLINE_30MIN = PERIOD.MIN_30.value     # 2
KLINE_1HOUR = PERIOD.MIN_60.value     # 3
KLINE_DAILY = PERIOD.DAILY.value      # 4
KLINE_WEEKLY = PERIOD.WEEKLY.value    # 5
KLINE_MONTHLY = PERIOD.MONTHLY.value  # 6
KLINE_EX_1MIN = PERIOD.MIN_1.value    # 7
KLINE_1MIN = PERIOD.MINS.value        # 8
KLINE_RI_K = PERIOD.DAYS.value        # 9
KLINE_3MONTH = PERIOD.QUARTERLY.value # 10
KLINE_YEARLY = PERIOD.YEARLY.value    # 11

# 分笔行情最多2000条
MAX_TRANSACTION_COUNT = 2000

# K线数据最多800条
MAX_KLINE_COUNT = 800

FREQUENCY = ['5m', '15m', '30m', '1h', 'day', 'week', 'mon', 'ex_1m', '1m', 'dk', '3mon', 'year']

# 板块相关
BLOCK_SZ = 'block_zs.dat'
BLOCK_FG = 'block_fg.dat'
BLOCK_GN = 'block_gn.dat'
BLOCK_DEFAULT = 'block.dat'

TYPE_FLATS = 0
TYPE_GROUP = 1

# 财务数据服务器（mootdx 独有）
GP_HOSTS = [
    ('默认财务数据线路', '120.76.152.87', 7709),
]

# 高级行情服务器（mootdx 独有）
HF_HOSTS = [
    ('上海双线高级行情1', '121.37.183.82', 7709),
    ('深圳双线高级行情1', '110.41.174.169', 7709),
]

CONFIG = {
    'SERVER': {'HQ': HQ_HOSTS, 'EX': EX_HOSTS, 'GP': GP_HOSTS, 'HF': HF_HOSTS},
    'BESTIP': {'HQ': '', 'EX': '', 'GP': '', 'HF': ''},
    'TDXDIR': 'C:/new_tdx',
}


def return_last_value(retry_state):
    """return the result of the last call attempt"""
    return retry_state.outcome.result()
