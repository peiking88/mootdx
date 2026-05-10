import datetime
from collections import OrderedDict

from opentdx import BLOCK_FILE_TYPE
from opentdx import MARKET
from opentdx import PERIOD
from opentdx import parse_tdx_date
from opentdx.client.quotationClient import QuotationClient
from opentdx.parser.quotation import CompanyCategory
from opentdx.parser.quotation import CompanyContent
from opentdx.parser.quotation import Finance
from opentdx.parser.quotation import XDXR

from mootdx.logger import logger


class StdHqAdapter:
    """opentdx 行情适配器"""

    def __init__(self, heartbeat=False, auto_retry=True, raise_exception=False, **kwargs):
        self._connected = False
        self._ip = None
        self._port = None
        self._client = QuotationClient(auto_retry=auto_retry, raise_exception=raise_exception)

    # -- 连接/生命周期 --

    def connect(self, ip, port, time_out=15):
        self._ip = ip
        self._port = int(port)

        result = self._client.connect(ip=str(self._ip), port=self._port, time_out=time_out)
        if result is None:
            return False
        if not self._client.login():
            return False
        self._connected = True
        return self

    def close(self):
        self._client.disconnect()
        self._connected = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @property
    def need_setup(self):
        return False

    @need_setup.setter
    def need_setup(self, value):
        pass

    @staticmethod
    def to_df(v):
        import pandas as pd

        if not v:
            return pd.DataFrame(data=None)
        if isinstance(v, list):
            return pd.DataFrame(data=v)
        return pd.DataFrame(data=None)

    # -- 类型转换 --

    def _convert_market(self, market):
        try:
            return MARKET(market)
        except ValueError:
            return MARKET.SH

    def _convert_period(self, category):
        try:
            return PERIOD(category)
        except ValueError:
            return PERIOD.DAILY

    # -- 数据方法 --

    def get_security_bars(self, category, market, code, start, count):
        result = self._client.get_kline(
            self._convert_market(market), code,
            self._convert_period(category),
            start=start, count=count,
        )
        if not result:
            return []

        items = []
        for bar in result:
            dt = bar.get('datetime')
            if dt:
                year, month, day = dt.year, dt.month, dt.day
                hour, minute = dt.hour, dt.minute
            else:
                year = month = day = hour = minute = 0

            items.append(OrderedDict([
                ('open', bar.get('open', 0)),
                ('high', bar.get('high', 0)),
                ('low', bar.get('low', 0)),
                ('close', bar.get('close', 0)),
                ('amount', bar.get('amount', 0)),
                ('volume', bar.get('vol', 0)),
                ('year', year),
                ('month', month),
                ('day', day),
                ('hour', hour),
                ('minute', minute),
                ('datetime', f'{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}'),
            ]))
        return items

    def get_index_bars(self, category, market, code, start, count):
        return self.get_security_bars(category, market, code, start, count)

    def get_security_quotes(self, all_stock=None, code=None):
        if code:
            all_stock = [(all_stock, code)]
        elif isinstance(all_stock, (list, tuple)) and len(all_stock) == 2 and isinstance(all_stock[0], int):
            all_stock = [all_stock]

        code_list = [(self._convert_market(m), c) for m, c in all_stock]
        result = self._client.get_stock_quotes_details(code_list)
        if not result:
            return []

        items = []
        for q in result:
            handicap = q.get('handicap', {})
            bids = handicap.get('bid', [])
            asks = handicap.get('ask', [])

            item = OrderedDict()
            mkt = q.get('market')
            item['market'] = mkt.value if hasattr(mkt, 'value') else mkt
            item['code'] = q.get('code', '')
            item['active1'] = q.get('active1', 0)
            item['price'] = q.get('close', 0)
            item['pre_close'] = q.get('pre_close', 0)
            item['open'] = q.get('open', 0)
            item['high'] = q.get('high', 0)
            item['low'] = q.get('low', 0)
            item['servertime'] = str(q.get('server_time', ''))
            item['volume'] = q.get('vol', 0)
            item['current_volume'] = q.get('cur_vol', 0)
            item['amount'] = q.get('amount', 0)
            item['sell_volume'] = q.get('s_vol', 0)
            item['buy_volume'] = q.get('b_vol', 0)

            for i in range(5):
                bid = bids[i] if i < len(bids) else {}
                ask = asks[i] if i < len(asks) else {}
                item[f'bid{i + 1}'] = bid.get('price', 0)
                item[f'ask{i + 1}'] = ask.get('price', 0)
                item[f'bid_vol{i + 1}'] = bid.get('vol', 0)
                item[f'ask_vol{i + 1}'] = ask.get('vol', 0)

            items.append(item)
        return items

    def get_security_count(self, market):
        return self._client.get_count(self._convert_market(market))

    def get_security_list(self, market, start):
        result = self._client.get_list(self._convert_market(market), start=start, count=1000)
        if not result:
            return []
        return [
            OrderedDict([
                ('code', item.get('code', '')),
                ('volunit', item.get('vol', 0)),
                ('decimal_point', item.get('decimal_point', 0)),
                ('name', item.get('name', '')),
                ('pre_close', item.get('pre_close', 0)),
            ])
            for item in result
        ]

    def get_history_minute_time_data(self, market, code, date):
        d = parse_tdx_date(date)
        result = self._client.get_tick_chart(self._convert_market(market), code, date=d)
        if not result:
            return []
        return [
            OrderedDict([
                ('price', t.get('price', 0)),
                ('volume', t.get('vol', 0)),
            ])
            for t in result
        ]

    def get_transaction_data(self, market, code, start, count):
        result = self._client.get_transaction(self._convert_market(market), code)
        if not result:
            return []
        action_map = {'BUY': 0, 'SELL': 1, 'NEUTRAL': 2}
        return [
            OrderedDict([
                ('time', f'{t["time"].hour:02d}:{t["time"].minute:02d}' if t.get('time') else ''),
                ('price', t.get('price', 0)),
                ('volume', t.get('vol', 0)),
                ('num', t.get('trans', 0)),
                ('direction', action_map.get(t.get('action', ''), 2)),
            ])
            for t in result
        ]

    def get_history_transaction_data(self, market, code, start, count, date):
        d = parse_tdx_date(date)
        if d is None:
            return []
        result = self._client.get_transaction(self._convert_market(market), code, date=d)
        if not result:
            return []
        action_map = {'BUY': 0, 'SELL': 1, 'NEUTRAL': 2}
        return [
            OrderedDict([
                ('time', f'{t["time"].hour:02d}:{t["time"].minute:02d}' if t.get('time') else ''),
                ('price', t.get('price', 0)),
                ('volume', t.get('vol', 0)),
                ('num', t.get('trans', 0)),
                ('direction', action_map.get(t.get('action', ''), 2)),
            ])
            for t in result
        ]

    def get_xdxr_info(self, market, code):
        result = self._client.call(XDXR(self._convert_market(market), code))
        if not result:
            return []

        name_to_cat = {
            '股本变化': 1, '除权除息': 2, '配股': 3, '红利': 4,
            '送股': 5, '转增': 6, '配股转增': 7, '增发': 8,
            '回购': 9, '权证': 10, '分离': 11, '权息': 12,
        }

        items = []
        for x in result:
            dt = x.get('date')
            items.append(OrderedDict([
                ('year', dt.year if dt else 0),
                ('month', dt.month if dt else 0),
                ('day', dt.day if dt else 0),
                ('category', name_to_cat.get(x.get('name', ''), 0)),
                ('name', x.get('name', '')),
                ('fenhong', x.get('fenhong')),
                ('peigujia', x.get('peigujia')),
                ('songzhuangu', x.get('songzhuangu')),
                ('peigu', x.get('peigu')),
                ('suogu', x.get('suogu')),
                ('panqianliutong', x.get('panqianliutong')),
                ('panhouliutong', x.get('panhouliutong')),
                ('qianzongguben', x.get('qianzongguben')),
                ('houzongguben', x.get('houzongguben')),
                ('fenshu', x.get('fenshu')),
                ('xingquanjia', x.get('xingquanjia')),
            ]))
        return items

    def get_finance_info(self, market, code):
        raw = self._client.call(Finance(self._convert_market(market), code))
        if not raw:
            return OrderedDict()

        x10k = lambda v: v * 10000 if isinstance(v, (int, float)) and v else v
        return OrderedDict([
            ('market', raw.get('market', market)),
            ('code', raw.get('code', code)),
            ('liutongguben', x10k(raw.get('liutongguben'))),
            ('province', raw.get('province', 0)),
            ('industry', raw.get('industry', '')),
            ('updated_date', raw.get('updated_date', 0)),
            ('ipo_date', raw.get('ipo_date', 0)),
            ('zongguben', x10k(raw.get('zongguben'))),
            ('guojiagu', x10k(raw.get('guojiagu'))),
            ('faqirenfarengu', x10k(raw.get('FaQiRenFaRenGu'))),
            ('farengu', x10k(raw.get('FaRenGu'))),
            ('bgu', x10k(raw.get('BGu'))),
            ('hgu', x10k(raw.get('HGu'))),
            ('zhigonggu', x10k(raw.get('MeiGuShouYi'))),
            ('zongzichan', x10k(raw.get('ZiChanZongJi'))),
            ('liudongzichan', x10k(raw.get('LiuDongZiChanZongJi'))),
            ('gudingzichan', x10k(raw.get('GuDingZiChanJinE'))),
            ('wuxingzichan', x10k(raw.get('WuXingZiChan'))),
            ('gudongrenshu', raw.get('GuDongRenShu', 0)),
            ('liudongfuzhai', x10k(raw.get('LiuDongFuZhaiHeJi'))),
            ('changqifuzhai', x10k(raw.get('changqifuzhai'))),
            ('zibengongjijin', x10k(raw.get('ZiBenGongJiJin'))),
            ('jingzichan', x10k(raw.get('GuiMuQuanYiHeJi'))),
            ('zhuyingshouru', x10k(raw.get('YinYeZongShouRu'))),
            ('zhuyinglirun', x10k(raw.get('YinYeChengBen'))),
            ('yingshouzhangkuan', x10k(raw.get('YingShouZhangKuan'))),
            ('yingyelirun', x10k(raw.get('YinYeLiRun'))),
            ('touzishouyu', x10k(raw.get('TouZiShouYi'))),
            ('jingyingxianjinliu', x10k(raw.get('JingYinXianJinLiuJinE'))),
            ('zongxianjinliu', x10k(raw.get('zongxianjinliu'))),
            ('cunhuo', x10k(raw.get('CunHuo'))),
            ('lirunzonghe', x10k(raw.get('LiRunZongE'))),
            ('shuihoulirun', x10k(raw.get('ShuiHouLiRun'))),
            ('jinglirun', x10k(raw.get('GuiMuJinLiRun'))),
            ('weifenpeilirun', x10k(raw.get('WeiFenLiRun'))),
            ('meigujingzichan', raw.get('MeiGuJinZiChan', 0)),
            ('baoliu2', raw.get('baoliu2', 0)),
        ])

    def get_company_info_category(self, market, code):
        result = self._client.call(CompanyCategory(self._convert_market(market), code))
        if not result:
            return []
        return [OrderedDict([(k, item.get(k, '')) for k in ('name', 'filename', 'start', 'length')]) for item in result]

    def get_company_info_content(self, market, code, filename, start, length):
        result = self._client.call(CompanyContent(self._convert_market(market), code, filename, start, length))
        return result if result else {}

    def get_and_parse_block_info(self, block_file):
        for bft in BLOCK_FILE_TYPE:
            if bft.value == block_file:
                return self._client.get_block_file(bft)
        return self._client.get_block_file(BLOCK_FILE_TYPE.DEFAULT)

    def get_traffic_stats(self):
        return None

    def get_report_file_by_size(self, filename, filesize=0, reporthook=None):
        return self._client.download_file(filename, filesize, reporthook)
