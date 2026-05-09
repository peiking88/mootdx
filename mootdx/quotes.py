import math
from datetime import datetime

import pandas as pd
from tenacity import retry
from tenacity import retry_if_exception_type
from tenacity import retry_if_result
from tenacity import stop_after_attempt
from tenacity import wait_random
from tqdm import tqdm

from mootdx import config
from mootdx.consts import MARKET_SH
from mootdx.consts import MARKET_SZ
from mootdx.consts import return_last_value
from mootdx.exceptions import MootdxValidationException
from mootdx.exhq_adapter import ExHqAdapter
from mootdx.hq_adapter import StdHqAdapter
from mootdx.logger import logger
from mootdx.server import bestip as check_bestip
from mootdx.utils import get_frequency
from mootdx.utils import get_stock_market
from mootdx.utils import get_stock_markets
from mootdx.utils import to_data

class Quotes(object):
    @staticmethod
    def factory(market='std', **kwargs):
        """
        股票市场 工厂方法

        :param market:  std 股票市场, ext 扩展市场， 默认股票市场
        :param kwargs:  可变参数
        :return: object
        """

        logger.debug(kwargs)

        if market == 'ext':
            return ExtQuotes(**kwargs)

        return StdQuotes(**kwargs)


def valid_server(server):
    import ipaddress

    if isinstance(server, tuple) or isinstance(server, list):
        try:
            address, port = server
            ipaddress.ip_address(address)
            return address, int(port)
        except (ValueError, TypeError) as e:
            raise ValueError(f'Server 格式错误: {e}')

    return None


class BaseQuotes(object):
    client = None
    bestip = None
    server = None

    verbose = False
    timeout = 15

    def __init__(self, server=None, bestip: bool = False, timeout: int = None, **kwargs) -> None:
        logger.debug('config.setup()')
        config.setup()

        logger.debug(f'server => {server}')
        self.server = valid_server(server)

        logger.debug(f'bestip => {bestip}')
        bestip and check_bestip(sync=True)

        self.timeout = timeout or 15
        logger.debug(f'timeout => {self.timeout}')

        self.verbose = kwargs.get('verbose', False)
        logger.debug(f'verbose => {self.verbose}')

    def __del__(self):
        logger.debug('call __del__')
        self.close()

    def reconnect(self):
        if self.closed:
            logger.debug('服务器连接已断开，正进行重新连接...')
            try:
                self.client.connect(*self.bestip)
            except Exception as ex:
                logger.error(f'重连失败: {ex}')

    def close(self):
        logger.debug('close')
        hasattr(self.client, 'close') and self.client.close()

    @property
    def closed(self) -> bool:
        try:
            if hasattr(self.client, '_connected'):
                return not self.client._connected
            return self.client.client is None or self.client.client._closed
        except (AttributeError, TypeError):
            return True

def auto_reconnect(func):
    def wrapper(self, *args, **kwargs):
        if self.closed:
            self.reconnect()
        return func(self, *args, **kwargs)
    return wrapper


def check_empty(value):
    """
    重试判断函数

    :param value: 要判断的值
    :return:
    """
    return value.empty if isinstance(value, pd.DataFrame) else not value


def _check_market(market):
    """验证市场代码为沪深市场"""
    if market not in [0, 1]:
        raise MootdxValidationException('市场代码错误, 目前只支持沪深市场')


# 非交易日补偿系数：全年约1/3天数非交易，用于日期差→交易天数粗略换算
_OFFSET_FACTOR_NEAR = 2.8   # 近期日期补偿
_OFFSET_FACTOR_FAR = 3.5    # 远期日期补偿


def _clamp_offset(offset, limit=800):
    return min(offset, limit)


def _market_from_symbol(symbol):
    return MARKET_SZ if symbol[:2] in ['00', '88', '99'] else MARKET_SH


class StdQuotes(BaseQuotes):
    """
    股票市场实时行情"""

    def __init__(self, server=None, bestip=False, timeout=15, heartbeat=False, auto_retry=True, raise_exception=False,
                 **kwargs):
        """构造函数

        :param bestip:  最佳 IP
        :param timeout: 超时时间
        :param kwargs:  可变参数
        """

        super().__init__(bestip=bestip, timeout=timeout, server=server, **kwargs)
        self.server and config.set('BESTIP', {'HQ': self.server})

        try:
            config.get('SERVER').get('HQ')[0]
        except ValueError as ex:
            logger.warning(ex)
        finally:
            default = config.get('SERVER').get('HQ')[0][1:]
            self.server = config.get('BESTIP').get('HQ') or default

        logger.debug(f'server: {self.server}')
        ip, port = self.server
        self.bestip = (ip, int(port))

        self.client = StdHqAdapter(heartbeat=heartbeat, auto_retry=auto_retry, raise_exception=raise_exception)
        self.client.connect(ip, int(port), time_out=timeout)

    def traffic(self):
        return self.client.get_traffic_stats()

    @auto_reconnect
    def quotes(self, symbol=None, **kwargs):
        """
        获取实时日行情数据

        :param symbol: 股票代码
        :return: pd.dataFrame or None
        """

        if not symbol:
            return to_data(None)

        if type(symbol) is str:
            symbol = [symbol]

        try:
            symbol = get_stock_markets(symbol)
            result = self.client.get_security_quotes(symbol)
        except MootdxValidationException:
            return to_data(None)

        return to_data(result, symbol=symbol, client=self, **kwargs)

    @auto_reconnect
    def bars(self, symbol='000001', frequency=9, start=0, offset=800, **kwargs):
        """
        获取实时日K线数据

        :param symbol: 股票代码
        :param frequency: 数据频次
        :param start: 开始位置
        :param offset: 每次获取条数
        :return: pd.dataFrame or None
        """
        frequency = get_frequency(frequency)
        market = get_stock_market(symbol)

        offset = _clamp_offset(offset)
        result = self.client.get_security_bars(int(frequency), int(market), str(symbol), int(start), int(offset))

        return to_data(result, symbol=symbol, client=self, **kwargs)

    @auto_reconnect
    def stock_count(self, market=MARKET_SH):
        """
        获取市场股票数量

        :param market: 股票市场代码 sh 上海， sz 深圳
        :return: pd.dataFrame or None
        """
        if market not in [0, 1, 2]:
            raise MootdxValidationException('市场代码错误')

        result = self.client.get_security_count(market=market)

        return result

    @auto_reconnect
    def stocks(self, market=MARKET_SH):
        """
        获取股票列表

        :param market: 股票市场
        :return:
        """

        _check_market(market)

        counts = self.stock_count(market=market)
        stocks = None

        if counts > 0:
            for start in tqdm(range(0, counts, 1000), ascii=True):
                result = self.client.get_security_list(market=market, start=start)
                stocks = pd.concat([stocks, to_data(result)], ignore_index=True) if start > 1 else to_data(result)

        return stocks

    def stock_all(self):
        stocks = None

        for m in [0, 1]:
            stocks = pd.concat([stocks, self.stocks(m)], ignore_index=True)

        return stocks

    @auto_reconnect
    def index_bars(self, symbol='000001', frequency=9, start=0, offset=800, **kwargs):
        """
        获取指数k线

        :param symbol: 股票代码
        :param frequency: 数据频次
        :param start: 开始位置
        :param offset: 获取数量
        :return:
        """

        frequency = get_frequency(frequency)
        offset = _clamp_offset(offset)

        market = _market_from_symbol(symbol)
        result = self.client.get_index_bars(int(frequency), int(market), str(symbol), int(start), int(offset))

        return to_data(result, symbol=symbol, client=self, **kwargs)

    @auto_reconnect
    def minute(self, symbol=None, **kwargs):
        """
        获取实时分时数据

        :param symbol: 股票代码
        :return: pd.DataFrame
        """

        today = datetime.now().strftime('%Y%m%d')
        return self.minutes(symbol=symbol, date=today, **kwargs)

    @auto_reconnect
    def minutes(self, symbol=None, date='20191023', **kwargs):
        """
        分时历史数据

        :param symbol:  股票代码
        :param date:    查询日期
        :return: pd.dataFrame or None
        """

        market = get_stock_market(symbol)

        _check_market(market)

        result = self.client.get_history_minute_time_data(market=market, code=symbol, date=date)

        return to_data(result, symbol=symbol, client=self, **kwargs)

    @auto_reconnect
    def transaction(self, symbol='', start=0, offset=800, **kwargs):
        """
        查询分笔成交

        :param symbol:  股票代码
        :param start:   起始位置
        :param offset:  结束位置
        :return: pd.dataFrame or None
        """

        market = get_stock_market(symbol)

        result = self.client.get_transaction_data(int(market), symbol, start, offset)

        return to_data(result, symbol=symbol, client=self, **kwargs)

    @auto_reconnect
    def transactions(self, symbol='', start=0, offset=800, date='20170209', **kwargs):
        """
        查询历史分笔成交

        :param symbol:  股票代码
        :param start:   起始位置
        :param offset:  获取数量
        :param date:    查询日期
        :return: pd.dataFrame or None
        """

        market = get_stock_market(symbol, string=False)

        _check_market(market)

        result = self.client.get_history_transaction_data(market, symbol, start, offset, int(date))
        return to_data(result, symbol=symbol, client=self, **kwargs)

    @auto_reconnect
    def F10C(self, symbol=''):  # noqa
        """
        查询公司信息目录

        :param symbol: 股票代码
        :return: pd.dataFrame or None
        """

        market = int(get_stock_market(symbol))

        _check_market(market)

        result = self.client.get_company_info_category(market, symbol)

        return result

    @auto_reconnect
    def F10(self, symbol='', name=''):  # noqa
        """
        读取公司信息详情

        :param name: 公司 F10 标题
        :param symbol: 股票代码
        :return: pd.dataFrame or None
        """

        result = {}
        market = int(get_stock_market(symbol, string=False))

        _check_market(market)

        category = self.client.get_company_info_category(market, symbol)

        if not category:
            return None

        if name:
            for x in category:
                if x['name'] == name:
                    return self.client.get_company_info_content(
                        market=market,
                        code=symbol,
                        filename=x['filename'],
                        start=x['start'],
                        length=x['length'],
                    )

        for x in category:
            result[x['name']] = self.client.get_company_info_content(
                market=market, code=symbol, filename=x['filename'], start=x['start'], length=x['length']
            )

        return result

    @auto_reconnect
    def xdxr(self, symbol='', **kwargs):
        """
        读取除权除息信息

        :param symbol: 股票代码
        :return: pd.dataFrame or None
        """

        market = get_stock_market(symbol)
        result = self.client.get_xdxr_info(int(market), symbol)

        return to_data(result, symbol=symbol, client=self, **kwargs)

    def get_factor(self, symbol='000001', adjust='qfq'):
        """获取复权因子序列。

        主路径：TDX 服务器 XDXR 数据 + AdjustmentFactorCrawler。
        备用路径：TX 数据为空或异常时回退到新浪财经。

        :param symbol: 股票代码
        :param adjust: 'qfq' (前复权) 或 'hfq' (后复权)
        :return: pd.DataFrame with columns [date, factor] (date为索引)
        """
        df = self._get_factor_from_tdx(symbol, adjust)
        if df is not None and not df.empty:
            return df

        logger.info(f"TDX factor empty for {symbol}, falling back to Sina")
        from mootdx.utils.factor import fetch_factor_from_sina
        return fetch_factor_from_sina(symbol, adjust)

    def _get_factor_from_tdx(self, symbol, adjust):
        """从 TDX 服务器获取复权因子（内部实现）。"""
        from opentdx.const import ADJUST
        from opentdx.crawler.adjustment_factor_crawler import AdjustmentFactorCrawler
        from opentdx.parser.quotation.company_info import XDXR
        from mootdx.utils import get_stock_market

        market = get_stock_market(symbol)
        try:
            raw_events = self.client._client.call(XDXR(int(market), symbol))
        except Exception as e:
            logger.warning(f"TDX XDXR fetch failed for {symbol}: {e}")
            return pd.DataFrame(columns=['date', 'factor'])

        if not raw_events:
            return pd.DataFrame(columns=['date', 'factor'])

        kline = self.get_k_data(symbol, '1990-01-01',
                               pd.Timestamp.now().strftime('%Y-%m-%d'))
        if kline is None or kline.empty:
            return pd.DataFrame(columns=['date', 'factor'])

        pre_close_prices = {}
        for evt in raw_events:
            d = evt.get('date')
            if d is None:
                continue
            if hasattr(d, 'strftime'):
                date_key = d.strftime('%Y-%m-%d')
            elif isinstance(d, pd.Timestamp):
                date_key = d.strftime('%Y-%m-%d')
            else:
                date_key = str(d)
            dt = pd.Timestamp(date_key)
            if 'date' in kline.columns:
                prev = kline[kline['date'] < dt]
            else:
                prev = kline[kline.index < dt]
            if not prev.empty:
                pre_close_prices[date_key] = float(prev.iloc[-1]['close'])

        adj_enum = ADJUST.QFQ if adjust == 'qfq' else ADJUST.HFQ
        results = AdjustmentFactorCrawler.compute_full_factor(
            raw_events, pre_close_prices, adj_enum)

        if not results:
            return pd.DataFrame(columns=['date', 'factor'])

        records = []
        for r in results:
            d = r.get('date')
            factor = r.get('factor')
            if d is None or factor is None:
                continue
            if hasattr(d, 'strftime'):
                d = d.strftime('%Y-%m-%d')
            elif isinstance(d, pd.Timestamp):
                d = d.strftime('%Y-%m-%d')
            records.append({'date': d, 'factor': factor})

        if not records:
            return pd.DataFrame(columns=['date', 'factor'])

        df = pd.DataFrame(records)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df = df.set_index('date').sort_index()
        return df

    @auto_reconnect
    def finance(self, symbol='000001', **kwargs):
        """
        读取财务信息

        :param symbol: 股票代码
        :return:
        """

        market = get_stock_market(symbol)
        result = self.client.get_finance_info(market=market, code=symbol)

        return to_data(result, symbol=symbol, client=self, **kwargs)

    @auto_reconnect
    def k(self, symbol='', begin=None, end=None, **kwargs):
        """
        读取k线信息

        :param symbol:  股票代码
        :param begin:   开始日期
        :param end:     截止日期
        :return: pd.dataFrame or None
        """

        result = self.get_k_data(symbol, begin, end)
        return to_data(result, symbol=symbol, **kwargs)

    def ohlc(self, **kwargs):
        return self.k(**kwargs)

    @auto_reconnect
    def get_k_data(self, code, start_date, end_date):
        # 开始时间离现在有几天
        first = (pd.to_datetime(end_date) - pd.to_datetime(datetime.now().date())).days
        first = (abs(first), 0)[first >= 0]

        # 结束时间离现在有几天
        last = (pd.to_datetime(start_date) - pd.to_datetime(datetime.now().date())).days
        last = (abs(last), 0)[last >= 0]

        # 去除节假日
        first -= int(first / _OFFSET_FACTOR_NEAR)
        last -= int(last / _OFFSET_FACTOR_FAR)

        temp = []
        market = get_stock_market(code)

        for i in range(math.ceil((last - first) / 800)):
            data = self.client.get_security_bars(9, market, code, (first + i * 800), 800)
            temp.append(self.client.to_df(data))

        data = pd.concat(temp)
        data = data.assign(date=data['datetime'].apply(lambda x: str(x)[0:10])).assign(code=str(code))
        data = data.set_index('date', drop=False, inplace=False)
        data = data.drop(['year', 'month', 'day', 'hour', 'minute', 'datetime'], axis=1)
        data = data.loc[(data.date >= start_date) & (data.date < end_date)]
        data = data.sort_index()

        return data

    @auto_reconnect
    def index(self, symbol='000001', frequency=9, start=0, offset=800, **kwargs):
        """
        获取指数k线

        K线种类:
        - 0 5分钟K线
        - 1 15分钟K线
        - 2 30分钟K线
        - 3 1小时K线
        - 4 日K线
        - 5 周K线
        - 6 月K线
        - 7 1分钟
        - 8 1分钟K线
        - 9 日K线
        - 10 季K线
        - 11 年K线

        :param symbol:      股票代码
        :param frequency:   数据频次
        :param market:      证券市场
        :param start:       开始位置
        :param offset:      每次获取条数
        :return: pd.dataFrame or None
        """
        frequency = get_frequency(frequency)

        offset = _clamp_offset(offset)
        market = _market_from_symbol(symbol)
        result = self.client.get_index_bars(int(frequency), int(market), str(symbol), int(start), int(offset))

        return to_data(result, symbol=symbol, client=self, **kwargs)

    def block(self, tofile='block.dat', **kwargs):
        """
        获取证券板块信息

        :param tofile: 保存文件
        :return: pd.dataFrame or None
        """

        result = self.client.get_and_parse_block_info(tofile)
        return to_data(result, **kwargs)

    def _get_sp_client(self):
        """获取或创建 SP 模式客户端（MAC 协议，用于板块/资金流向）

        SP 模式需要连接支持 MAC 协议的服务器，普通 TDX 服务器不支持。
        """
        if not hasattr(self, '_sp_client') or self._sp_client is None:
            from opentdx.client.quotationClient import QuotationClient
            from opentdx.const import mac_hosts

            self._sp_client = QuotationClient(auto_retry=True, raise_exception=False)
            self._sp_client.connect(ip=mac_hosts[0][1], port=mac_hosts[0][2])
            self._sp_client.login()
            self._sp_client.sp(hosts=mac_hosts)
        return self._sp_client

    def board_list(self, board_type=None, count=10000, **kwargs):
        """
        获取板块列表

        :param board_type: 板块类型，如 'industry'（行业）, 'concept'（概念）, 'style'（风格）, 'region'（地区）
        :param count: 获取数量
        :return: pd.DataFrame
        """
        from opentdx import BOARD_TYPE

        type_map = {
            'industry': BOARD_TYPE.HY, 'industry2': BOARD_TYPE.HY2,
            'concept': BOARD_TYPE.GN, 'style': BOARD_TYPE.FG,
            'region': BOARD_TYPE.DQ, 'other': BOARD_TYPE.OTHER,
            'all': BOARD_TYPE.ALL,
        }
        bt = type_map.get(board_type, BOARD_TYPE.HY) if board_type else BOARD_TYPE.HY
        sp = self._get_sp_client()
        result = sp.get_board_list(bt, count=count)
        return to_data(result, **kwargs)

    def board_quotes(self, board_symbol, count=20, sort_type=None, sort_order=None, **kwargs):
        """
        获取板块成分股行情

        :param board_symbol: 板块代码，如 '880001'
        :param count: 获取数量
        :param sort_type: 排序字段（opentdx SORT_TYPE 枚举）
        :param sort_order: 排序方向（opentdx SORT_ORDER 枚举）
        :return: pd.DataFrame
        """
        from opentdx import SORT_TYPE
        from opentdx.const import SORT_ORDER

        sp = self._get_sp_client()
        result = sp.get_board_members_quotes(
            board_symbol, count=count,
            sort_type=sort_type or SORT_TYPE.CHANGE_PCT,
            sort_order=sort_order or SORT_ORDER.DESC,
        )
        return to_data(result, **kwargs)

    def capital_flow(self, symbol, **kwargs):
        """
        获取个股资金流向

        :param symbol: 股票代码
        :return: pd.DataFrame
        """
        from opentdx import MARKET

        market = get_stock_market(symbol, string=False)
        sp = self._get_sp_client()
        result = sp.get_symbol_zjlx(symbol, MARKET(market))
        return to_data(result, **kwargs)

    def stock_ranking(self, category=None, **kwargs):
        """
        获取排行榜数据（涨停/跌幅/振幅/涨速等）

        :param category: 排行类别（opentdx CATEGORY 枚举），默认全部A股
        :return: dict
        """
        from opentdx import CATEGORY

        cat = category or CATEGORY.A
        result = self.client._client.get_stock_top_board(cat)
        return result

    def stock_list_sorted(self, category=None, sort_type=None, count=80, filter_types=None, **kwargs):
        """
        获取带排序筛选的股票列表

        :param category: 股票类别（opentdx CATEGORY 枚举），默认全部A股
        :param sort_type: 排序字段（opentdx SORT_TYPE 枚举）
        :param count: 获取数量
        :param filter_types: 筛选类型列表（opentdx FILTER_TYPE 枚举）
        :return: pd.DataFrame
        """
        from opentdx import CATEGORY, SORT_TYPE

        cat = category or CATEGORY.A
        st = sort_type or SORT_TYPE.CHANGE_PCT
        result = self.client._client.get_stock_quotes_list(cat, start=0, count=count, sort_type=st, filter=filter_types)
        return to_data(result, **kwargs)

    def auction(self, symbol, **kwargs):
        """
        获取集合竞价数据

        :param symbol: 股票代码
        :return: pd.DataFrame
        """
        from opentdx import MARKET

        market = get_stock_market(symbol, string=False)
        result = self.client._client.get_auction(MARKET(market), symbol)
        return to_data(result, **kwargs)

    def unusual(self, market=0, **kwargs):
        """
        获取异动预警数据

        :param market: 市场代码（0=深市, 1=沪市）
        :return: pd.DataFrame
        """
        from opentdx import MARKET

        result = self.client._client.get_unusual(MARKET(market))
        return to_data(result, **kwargs)

    def vol_profile(self, symbol, **kwargs):
        """
        获取成交分布数据

        :param symbol: 股票代码
        :return: pd.DataFrame
        """
        from opentdx import MARKET

        market = get_stock_market(symbol, string=False)
        result = self.client._client.get_vol_profile(MARKET(market), symbol)
        return to_data(result, **kwargs)

    def index_info(self, symbol_list, **kwargs):
        """
        获取指数行情

        :param symbol_list: 指数代码列表，如 ['000001', '399001']
        :return: pd.DataFrame
        """
        from opentdx import MARKET

        code_list = []
        for s in symbol_list:
            market = (MARKET_SZ, MARKET_SH)[s[:2] in ['00', '88', '99']]
            code_list.append((MARKET(market), s))
        result = self.client._client.get_index_info(code_list)
        return to_data(result, **kwargs)

    def _fq_bars(self, symbol='000001', frequency=9, start=0, offset=800, type_='01', **kwargs):
        raw = self.bars(symbol=symbol, frequency=frequency, start=start, offset=offset, **kwargs)
        if raw is None or raw.empty:
            return raw
        xdxr = self.xdxr(symbol=symbol)
        if xdxr is None or xdxr.empty:
            return raw

        from mootdx.tools.reversion import reversion
        return reversion(symbol, raw, xdxr, type_=type_)

    def qfq_bars(self, symbol='000001', frequency=9, start=0, offset=800, **kwargs):
        """获取前复权K线数据。自动获取除权数据并复权。"""
        return self._fq_bars(symbol, frequency, start, offset, type_='01', **kwargs)

    def hfq_bars(self, symbol='000001', frequency=9, start=0, offset=800, **kwargs):
        """获取后复权K线数据。自动获取除权数据并复权。"""
        return self._fq_bars(symbol, frequency, start, offset, type_='02', **kwargs)


_retry = retry(
    wait=wait_random(min=1, max=10),
    stop=stop_after_attempt(3),
    retry_error_callback=return_last_value,
    retry=(retry_if_exception_type() | retry_if_result(check_empty)),
)


class ExtQuotes(BaseQuotes):
    """扩展市场实时行情"""

    # server = ("112.74.214.43", 7727)

    def __init__(self, server: list = None, bestip=False, timeout=15, **kwargs):
        """
        构造函数

        :param bestip:  最优服务器IP
        :param timeout: 超时时间
        :param kwargs:  可变参数
        """
        super().__init__(bestip=bestip, timeout=timeout, server=server, **kwargs)
        self.server and config.set('BESTIP', {'EX': self.server})

        try:
            config.get('SERVER').get('EX')[0]
        except ValueError as ex:
            logger.warning(ex)
        finally:
            default = config.get('SERVER').get('EX')[0]
            self.server = config.get('BESTIP').get('EX') or default

        for x in ['verbose', 'server', 'quiet']:
            if x in kwargs.keys():
                del kwargs[x]

        try:
            self.client = ExHqAdapter(raise_exception=False, auto_retry=True, **kwargs)
            self.client.connect(*self.server)
        except Exception:  # noqa
            logger.error('服务器连接超时.')

    @staticmethod
    def validate(market, symbol):
        """
        验证股票市场。支持整数或 EX_CATEGORY 枚举。

        EX_CATEGORY 枚举值:
          HK=31(香港主板), HK_GEM=48(香港创业板), GGT=71(港股通),
          US=74(美股), HSI=12001(恒指成分股), HSHC=12002(恒生红筹),
          HSGQ=12004(恒生国企), HSGZ=12007(恒生国指), HSKJ=12012(恒生科技),
          USZGG=13001(美股中概股), USZM=13002(知名美股)

        :param market: 市场代码（int）或 EX_CATEGORY 枚举
        :param symbol: 股票代码
        :return: tuple (market_code, symbol)
        """
        from opentdx.const import EX_CATEGORY

        if not market:
            if len(symbol.split('#')) > 1:
                market = symbol.split('#')[0]
                symbol = symbol.split('#')[1]

        if not market:
            raise ValueError('市场参数错误, 市场参数不能为空.')

        if isinstance(market, EX_CATEGORY):
            market = market.value[0] if isinstance(market.value, tuple) else market.value

        return int(market), symbol

    @_retry
    def markets(self, **kwargs):
        """
        获取实时市场列表

        :return: pd.dataFrame or None
        """

        result = self.client.get_markets()
        return to_data(result, **kwargs)

    @_retry
    def instrument(self, start=0, offset=800, **kwargs):
        """
        查询代码列表

        :param start:   开始位置
        :param offset:  获取数量
        :return:
        """

        result = self.client.get_instrument_info(start=start, count=offset)
        return to_data(result, **kwargs)

    @_retry
    def instrument_count(self):
        """
        市场商品数量

        :return:
        """

        result = self.client.get_instrument_count()

        return result

    @_retry
    def instruments(self, **kwargs):
        """
        查询所有代码列表

        :return:
        """

        result = []

        count = self.client.get_instrument_count()
        pages = math.ceil(count / 100)

        for page in tqdm(range(0, pages), ascii=True):
            result += self.client.get_instrument_info(page * 100, 100)

        return to_data(result, **kwargs)

    @_retry
    def quote(self, market='', symbol='', **kwargs):
        """
        查询五档行情

        :param market: 市场ID
        :param symbol: 证券代码
        :return:
        """

        market, symbol = self.validate(market, symbol)
        result = self.client.get_instrument_quote(market, symbol)

        return to_data(result, symbol=symbol, client=self, **kwargs)

    @_retry
    def minute(self, market='', symbol='', **kwargs):
        """
        查询分时行情

        :param market: 市场ID
        :param symbol: 证券代码
        :return:
        """

        market, symbol = self.validate(market, symbol)
        result = self.client.get_minute_time_data(market, symbol)

        return to_data(result, symbol=symbol, client=self, **kwargs)

    @_retry
    def minutes(self, market=None, symbol='', date='', **kwargs):
        """
        查询历史分时行情

        :param market:  市场ID
        :param symbol:  证券代码
        :param date:    查询日期
        :return:
        """

        market, symbol = self.validate(market, symbol)
        result = self.client.get_history_minute_time_data(market, symbol, date)

        return to_data(result, symbol=symbol, client=self, **kwargs)

    @_retry
    def bars(self, frequency='', market='', symbol='', start=0, offset=800, **kwargs):
        """
        查询k线数据

        :param frequency: 数据频次, K线周期
        :param market: 市场ID
        :param symbol: 证券代码
        :param start:  起始位置
        :param offset: 获取数量
        :return:
        """

        frequency = get_frequency(frequency)
        market, symbol = self.validate(market, symbol)
        result = self.client.get_instrument_bars(
            category=frequency, market=market, code=symbol, start=start, count=offset
        )

        return to_data(result, symbol=symbol, **kwargs)

    @_retry
    def transaction(self, market=None, symbol='', start=0, offset=800, **kwargs):
        """
        查询分笔成交

        :param market: 市场ID
        :param symbol: 证券代码
        :param start:  开始位置
        :param offset: 获取数量
        :return:
        """

        market, symbol = self.validate(market, symbol)
        result = self.client.get_transaction_data(market=market, code=symbol, start=start, count=offset)

        return to_data(result, symbol=symbol, client=self, **kwargs)

    @_retry
    def transactions(self, market=None, symbol='', date='', start=0, offset=800, **kwargs):
        """
        查询历史分笔成交

        :param market:  市场ID
        :param symbol:  证券代码
        :param date:    查询日期
        :param start:   开始位置
        :param offset:  获取数量
        :return:
        """

        market, symbol = self.validate(market, symbol)
        result = self.client.get_history_transaction_data(
            market=market, code=symbol, date=int(date), start=start, count=offset
        )

        return to_data(result, symbol=symbol, client=self, **kwargs)
