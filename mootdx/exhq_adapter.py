import datetime
from collections import OrderedDict

from mootdx.logger import logger


class ExHqAdapter:
    """兼容 tdxpy TdxExHq_API 接口的 opentdx 适配器，优先使用 opentdx 新协议"""

    def __init__(self, **kwargs):
        self._connected = False
        self._ip = None
        self._port = None

        try:
            from opentdx.client import exQuotationClient

            self._client = exQuotationClient(auto_retry=True, raise_exception=False)
            self._backend = 'opentdx'
        except ImportError:
            from tdxpy.exhq import TdxExHq_API

            self._client = TdxExHq_API(
                auto_retry=kwargs.pop('auto_retry', True),
                raise_exception=kwargs.pop('raise_exception', False),
                **kwargs,
            )
            self._backend = 'tdxpy'

    def connect(self, *args, **kwargs):
        # 支持 (ip, port) 和 (name, ip, port) 两种格式
        if len(args) == 3:
            _, ip, port = args
        elif len(args) == 2:
            ip, port = args
        else:
            raise ValueError(f'Expected (ip, port) or (name, ip, port), got {len(args)} args')

        self._ip = ip
        self._port = int(port)

        if self._backend == 'opentdx':
            connect_kwargs = {}
            if 'time_out' in kwargs:
                connect_kwargs['time_out'] = kwargs['time_out']
            result = self._client.connect(ip=str(self._ip), port=self._port, **connect_kwargs)
            if result is None:
                return False
            if not self._client.login():
                return False
            self._connected = True
            return self
        else:
            return self._client.connect(str(self._ip), self._port, **kwargs)

    def close(self):
        if self._backend == 'opentdx':
            self._client.disconnect()
        else:
            self._client.close()
        self._connected = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _convert_market(self, market):
        from opentdx import EX_MARKET

        try:
            return EX_MARKET(market)
        except ValueError:
            return EX_MARKET.CFFEX_FUTURES

    def _convert_period(self, category):
        from opentdx import PERIOD

        try:
            return PERIOD(category)
        except ValueError:
            return PERIOD.DAILY

    @staticmethod
    def _parse_date(date):
        if date is None or date == '':
            return None
        if isinstance(date, datetime.date):
            return date
        if isinstance(date, int) and date > 0:
            s = str(date)
            return datetime.date(int(s[:4]), int(s[4:6]), int(s[6:8]))
        return None

    def get_markets(self):
        if self._backend == 'opentdx':
            result = self._client.get_category_list()
            if not result:
                return []
            return [
                OrderedDict([
                    ('market', item.get('code', 0)),
                    ('category', item.get('code', 0)),
                    ('name', item.get('name', '')),
                    ('short_name', item.get('abbr', '')),
                ])
                for item in result
            ]
        return self._client.get_markets()

    def get_instrument_count(self):
        if self._backend == 'opentdx':
            return self._client.get_count()
        return self._client.get_instrument_count()

    def get_instrument_info(self, start, count):
        if self._backend == 'opentdx':
            result = self._client.get_list(start=start, count=count)
            if not result:
                return []
            return [
                OrderedDict([
                    ('market', item.get('market', 0)),
                    ('category', item.get('category', 0)),
                    ('code', item.get('code', '')),
                    ('name', item.get('name', '')),
                    ('desc', item.get('desc', '')),
                ])
                for item in result
            ]
        return self._client.get_instrument_info(start, count)

    def get_instrument_quote(self, market, code):
        if self._backend == 'opentdx':
            result = self._client.get_quotes_single(self._convert_market(market), code)
            if not result:
                return []

            q = result
            handicap = q.get('handicap', {})
            bids = handicap.get('bids', [])
            asks = handicap.get('asks', [])

            item = OrderedDict()
            item['market'] = market
            item['code'] = code
            item['pre_close'] = q.get('pre_close', 0)
            item['open'] = q.get('open', 0)
            item['high'] = q.get('high', 0)
            item['low'] = q.get('low', 0)
            item['price'] = q.get('close', 0)
            item['kaicang'] = q.get('open_position', 0)
            item['zongliang'] = q.get('vol', 0)
            item['xianliang'] = q.get('curr_vol', 0)
            item['neipan'] = q.get('in_vol', 0)
            item['waipan'] = q.get('out_vol', 0)
            item['chicang'] = q.get('hold_position', 0)

            for i in range(5):
                bid = bids[i] if i < len(bids) else {}
                ask = asks[i] if i < len(asks) else {}
                item[f'bid{i + 1}'] = bid.get('price', 0)
                item[f'bid_vol{i + 1}'] = bid.get('vol', 0)
                item[f'ask{i + 1}'] = ask.get('price', 0)
                item[f'ask_vol{i + 1}'] = ask.get('vol', 0)

            return [item]
        return self._client.get_instrument_quote(market, code)

    def get_instrument_bars(self, category, market, code, start=0, count=700):
        if self._backend == 'opentdx':
            result = self._client.get_kline(
                self._convert_market(market), code,
                self._convert_period(category),
                start=start, count=count,
            )
            if not result:
                return []

            items = []
            for bar in result:
                dt = bar.get('date_time')
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
                    ('position', 0),
                    ('trade', bar.get('vol', 0)),
                    ('price', bar.get('close', 0)),
                    ('year', year),
                    ('month', month),
                    ('day', day),
                    ('hour', hour),
                    ('minute', minute),
                    ('datetime', f'{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}'),
                    ('amount', bar.get('amount', 0)),
                ]))
            return items
        return self._client.get_instrument_bars(category, market, code, start, count)

    def get_minute_time_data(self, market, code):
        if self._backend == 'opentdx':
            result = self._client.get_tick_chart(self._convert_market(market), code)
            if not result:
                return []

            items = []
            for tick in result:
                t = tick.get('time')
                items.append(OrderedDict([
                    ('hour', t.hour if t else 0),
                    ('minute', t.minute if t else 0),
                    ('price', tick.get('price', 0)),
                    ('avg_price', tick.get('avg', 0)),
                    ('volume', tick.get('vol', 0)),
                    ('open_interest', 0),
                ]))
            return items
        return self._client.get_minute_time_data(market, code)

    def get_history_minute_time_data(self, market, code, date):
        if self._backend == 'opentdx':
            d = self._parse_date(date)
            result = self._client.get_tick_chart(self._convert_market(market), code, d)
            if not result:
                return []

            items = []
            for tick in result:
                t = tick.get('time')
                items.append(OrderedDict([
                    ('hour', t.hour if t else 0),
                    ('minute', t.minute if t else 0),
                    ('price', tick.get('price', 0)),
                    ('avg_price', tick.get('avg', 0)),
                    ('volume', tick.get('vol', 0)),
                    ('open_interest', 0),
                ]))
            return items
        return self._client.get_history_minute_time_data(market, code, date)

    def _convert_transactions(self, result, d):
        if not result:
            return []

        items = []
        for txn in result:
            t = txn.get('time')
            action = txn.get('action', 'NEUTRAL')
            direction = {'BUY': 1, 'SELL': -1}.get(action, 0)
            nature_name = {'BUY': '外盘', 'SELL': '内盘'}.get(action, '')
            items.append(OrderedDict([
                ('date', datetime.datetime.combine(d, t) if t else None),
                ('hour', t.hour if t else 0),
                ('minute', t.minute if t else 0),
                ('price', txn.get('price', 0)),
                ('volume', txn.get('vol', 0)),
                ('zengcang', 0),
                ('nature', 0),
                ('nature_name', nature_name),
                ('direction', direction),
            ]))
        return items

    def get_transaction_data(self, market, code, start=0, count=1800):
        if self._backend == 'opentdx':
            m = self._convert_market(market)
            today = datetime.date.today()
            # 尝试今天及最近几个交易日
            for offset in range(7):
                d = today - datetime.timedelta(days=offset)
                result = self._client.get_history_transaction(m, code, d)
                if result:
                    return self._convert_transactions(result, d)
            return []
        return self._client.get_transaction_data(market, code, start, count)

    def get_history_transaction_data(self, market, code, date, start=0, count=1800):
        if self._backend == 'opentdx':
            d = self._parse_date(date)
            if d is None:
                return []
            result = self._client.get_history_transaction(self._convert_market(market), code, d)
            return self._convert_transactions(result, d)
        return self._client.get_history_transaction_data(market, code, date, start, count)
