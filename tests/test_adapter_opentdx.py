"""测试 StdHqAdapter / ExHqAdapter 在 opentdx 后端下的方法委托"""
from collections import OrderedDict
from unittest import mock

import pytest

from mootdx.hq_adapter import StdHqAdapter
from mootdx.exhq_adapter import ExHqAdapter


def make_hq_adapter():
    """创建 StdHqAdapter 并注入 mock opentdx 客户端"""
    adapter = StdHqAdapter.__new__(StdHqAdapter)
    mock_client = mock.MagicMock()
    adapter._client = mock_client
    adapter._connected = True
    adapter._ip = '1.2.3.4'
    adapter._port = 7709
    return adapter, mock_client


def make_exhq_adapter():
    """创建 ExHqAdapter 并注入 mock opentdx 客户端"""
    adapter = ExHqAdapter.__new__(ExHqAdapter)
    mock_client = mock.MagicMock()
    adapter._client = mock_client
    adapter._connected = True
    adapter._ip = '1.2.3.4'
    adapter._port = 7727
    return adapter, mock_client


class TestStdHqDelegation:
    def _adapter(self):
        return make_hq_adapter()

    def test_get_security_bars(self):
        from opentdx import MARKET, PERIOD
        ad, cl = self._adapter()
        cl.get_kline.return_value = [{'datetime': None, 'open': 10, 'high': 11, 'low': 9, 'close': 10, 'amount': 100, 'vol': 50}]
        result = ad.get_security_bars(9, 0, '000001', 0, 100)
        cl.get_kline.assert_called_once_with(MARKET.SZ, '000001', PERIOD.DAYS, start=0, count=100)
        assert len(result) == 1
        assert result[0]['open'] == 10

    def test_get_index_bars(self):
        from opentdx import MARKET, PERIOD
        ad, cl = self._adapter()
        cl.get_kline.return_value = [{'datetime': None, 'open': 11, 'high': 12, 'low': 10, 'close': 11, 'amount': 200, 'vol': 80}]
        result = ad.get_index_bars(9, 1, '000001', 0, 100)
        cl.get_kline.assert_called_once_with(MARKET.SH, '000001', PERIOD.DAYS, start=0, count=100)
        assert result[0]['open'] == 11

    def test_get_security_quotes(self):
        from opentdx import MARKET
        ad, cl = self._adapter()
        cl.get_stock_quotes_details.return_value = [
            {'market': MARKET.SZ, 'code': '000001', 'close': 10, 'pre_close': 9,
             'open': 9.5, 'high': 10.5, 'low': 9, 'server_time': '',
             'vol': 1000, 'cur_vol': 500, 'amount': 10000, 's_vol': 0, 'b_vol': 0,
             'active1': 0, 'handicap': {'bid': [], 'ask': []}}
        ]
        result = ad.get_security_quotes([(0, '000001')])
        cl.get_stock_quotes_details.assert_called_once()
        assert result[0]['code'] == '000001'

    def test_get_security_count(self):
        from opentdx import MARKET
        ad, cl = self._adapter()
        cl.get_count.return_value = 5000
        result = ad.get_security_count(0)
        cl.get_count.assert_called_once_with(MARKET.SZ)
        assert result == 5000

    def test_get_security_list(self):
        from opentdx import MARKET
        ad, cl = self._adapter()
        cl.get_list.return_value = [{'code': '000001', 'name': '平安银行', 'pre_close': 10, 'vol': 100, 'decimal_point': 2}]
        result = ad.get_security_list(0, 0)
        cl.get_list.assert_called_once_with(MARKET.SZ, start=0, count=1000)
        assert result[0]['code'] == '000001'

    def test_get_history_minute_time_data(self):
        from opentdx import MARKET
        ad, cl = self._adapter()
        cl.get_tick_chart.return_value = [{'price': 10, 'vol': 100}]
        result = ad.get_history_minute_time_data(0, '000001', 20240101)
        cl.get_tick_chart.assert_called_once()
        assert result[0]['price'] == 10

    def test_get_transaction_data(self):
        from opentdx import MARKET
        ad, cl = self._adapter()
        cl.get_transaction.return_value = [{'time': None, 'price': 10, 'vol': 100, 'trans': 1, 'action': 'BUY'}]
        result = ad.get_transaction_data(0, '000001', 0, 100)
        cl.get_transaction.assert_called_once_with(MARKET.SZ, '000001')
        assert result[0]['price'] == 10

    def test_get_history_transaction_data(self):
        from opentdx import MARKET
        ad, cl = self._adapter()
        cl.get_transaction.return_value = [{'time': None, 'price': 10, 'vol': 100, 'trans': 1, 'action': 'SELL'}]
        result = ad.get_history_transaction_data(0, '000001', 0, 100, 20240101)
        cl.get_transaction.assert_called_once_with(MARKET.SZ, '000001', date=mock.ANY)
        assert result[0]['price'] == 10

    def test_get_xdxr_info(self):
        from opentdx import MARKET
        from opentdx.parser.quotation import XDXR
        ad, cl = self._adapter()
        cl.call.return_value = [{'date': None, 'name': '除权除息', 'fenhong': None, 'peigujia': None,
                                  'songzhuangu': None, 'peigu': None, 'suogu': None,
                                  'panqianliutong': None, 'panhouliutong': None,
                                  'qianzongguben': None, 'houzongguben': None,
                                  'fenshu': None, 'xingquanjia': None}]
        result = ad.get_xdxr_info(0, '000001')
        cl.call.assert_called_once()
        assert result[0]['name'] == '除权除息'

    def test_get_finance_info(self):
        from opentdx import MARKET
        from opentdx.parser.quotation import Finance
        ad, cl = self._adapter()
        cl.call.return_value = OrderedDict([('market', 0), ('code', '000001')])
        result = ad.get_finance_info(0, '000001')
        cl.call.assert_called_once()
        assert result['code'] == '000001'

    def test_get_company_info_category(self):
        from opentdx import MARKET
        from opentdx.parser.quotation import CompanyCategory
        ad, cl = self._adapter()
        cl.call.return_value = [{'name': 'test', 'filename': 'f.txt', 'start': 0, 'length': 100}]
        result = ad.get_company_info_category(0, '000001')
        cl.call.assert_called_once()
        assert result[0]['name'] == 'test'

    def test_get_company_info_content(self):
        from opentdx import MARKET
        from opentdx.parser.quotation import CompanyContent
        ad, cl = self._adapter()
        cl.call.return_value = {'content': 'data'}
        result = ad.get_company_info_content(0, '000001', 'file.txt', 0, 100)
        cl.call.assert_called_once()
        assert result == {'content': 'data'}

    def test_get_and_parse_block_info(self):
        ad, cl = self._adapter()
        cl.get_block_file.return_value = [{'name': 'block'}]
        result = ad.get_and_parse_block_info('block.dat')
        cl.get_block_file.assert_called_once()
        assert result == [{'name': 'block'}]

    def test_get_traffic_stats(self):
        ad, cl = self._adapter()
        result = ad.get_traffic_stats()
        assert result is None

    def test_get_report_file_by_size(self):
        ad, cl = self._adapter()
        cl.download_file.return_value = True
        result = ad.get_report_file_by_size('report.dat', 1024, None)
        cl.download_file.assert_called_once_with('report.dat', 1024, None)
        assert result is True


class TestExHqDelegation:
    def _adapter(self):
        return make_exhq_adapter()

    def test_get_markets(self):
        from opentdx import EX_MARKET
        ad, cl = self._adapter()
        cl.get_category_list.return_value = [{'code': 47, 'name': '沪深300', 'abbr': 'IF'}]
        result = ad.get_markets()
        cl.get_category_list.assert_called_once()
        assert result[0]['name'] == '沪深300'

    def test_get_instrument_count(self):
        ad, cl = self._adapter()
        cl.get_count.return_value = 500
        result = ad.get_instrument_count()
        cl.get_count.assert_called_once()
        assert result == 500

    def test_get_instrument_info(self):
        ad, cl = self._adapter()
        cl.get_list.return_value = [{'market': 47, 'category': 1, 'code': 'IFL0', 'name': 'IFL0', 'desc': '沪深300'}]
        result = ad.get_instrument_info(0, 100)
        cl.get_list.assert_called_once_with(start=0, count=100)
        assert result[0]['code'] == 'IFL0'

    def test_get_instrument_quote(self):
        from opentdx import EX_MARKET
        ad, cl = self._adapter()
        cl.get_quotes_single.return_value = {
            'pre_close': 5000, 'open': 5010, 'high': 5020, 'low': 4990,
            'close': 5015, 'open_position': 0, 'vol': 1000, 'curr_vol': 100,
            'in_vol': 500, 'out_vol': 500, 'hold_position': 0,
            'handicap': {'bids': [], 'asks': []},
        }
        result = ad.get_instrument_quote(47, 'IFL0')
        cl.get_quotes_single.assert_called_once()
        assert result[0]['price'] == 5015

    def test_get_instrument_bars(self):
        from opentdx import EX_MARKET, PERIOD
        ad, cl = self._adapter()
        cl.get_kline.return_value = [{'date_time': None, 'open': 5000, 'high': 5010, 'low': 4990, 'close': 5005, 'vol': 100, 'amount': 0}]
        result = ad.get_instrument_bars(9, 47, 'IFL0', 0, 100)
        cl.get_kline.assert_called_once_with(EX_MARKET(47), 'IFL0', PERIOD.DAYS, start=0, count=100)
        assert result[0]['open'] == 5000

    def test_get_minute_time_data(self):
        from opentdx import EX_MARKET
        ad, cl = self._adapter()
        cl.get_tick_chart.return_value = [{'time': None, 'price': 5000, 'avg': 5000, 'vol': 100}]
        result = ad.get_minute_time_data(47, 'IFL0')
        cl.get_tick_chart.assert_called_once()
        assert result[0]['price'] == 5000

    def test_get_history_minute_time_data(self):
        from opentdx import EX_MARKET
        ad, cl = self._adapter()
        cl.get_tick_chart.return_value = [{'time': None, 'price': 5000, 'avg': 5000, 'vol': 100}]
        result = ad.get_history_minute_time_data(47, 'IFL0', 20240101)
        cl.get_tick_chart.assert_called_once()
        assert result[0]['price'] == 5000

    def test_get_transaction_data(self):
        from opentdx import EX_MARKET
        ad, cl = self._adapter()
        cl.get_history_transaction.return_value = [{'time': None, 'price': 5000, 'vol': 10, 'action': 'BUY'}]
        with mock.patch.object(ad, '_convert_transactions', return_value=[OrderedDict([('price', 5000)])]):
            result = ad.get_transaction_data(47, 'IFL0')
        assert result[0]['price'] == 5000

    def test_get_history_transaction_data(self):
        from opentdx import EX_MARKET
        ad, cl = self._adapter()
        cl.get_history_transaction.return_value = [{'time': None, 'price': 5000, 'vol': 10, 'action': 'SELL'}]
        with mock.patch.object(ad, '_convert_transactions', return_value=[OrderedDict([('price', 5000)])]):
            result = ad.get_history_transaction_data(47, 'IFL0', 20240101)
        assert result[0]['price'] == 5000


class TestExHqConnect:
    def test_connect_opentdx_backend(self):
        adapter = ExHqAdapter.__new__(ExHqAdapter)
        mock_client = mock.MagicMock()
        mock_client.connect.return_value = True
        mock_client.login.return_value = True
        adapter._client = mock_client

        result = adapter.connect('1.2.3.4', 7727, time_out=5)
        mock_client.connect.assert_called_once_with(ip='1.2.3.4', port=7727, time_out=5)
        assert result == adapter
        assert adapter._ip == '1.2.3.4'
        assert adapter._port == 7727

    def test_close_opentdx_backend(self):
        adapter = ExHqAdapter.__new__(ExHqAdapter)
        mock_client = mock.MagicMock()
        adapter._client = mock_client
        adapter._connected = True

        adapter.close()
        mock_client.disconnect.assert_called_once()
        assert adapter._connected is False


class TestStdHqConnect:
    def test_connect_opentdx_backend(self):
        adapter = StdHqAdapter.__new__(StdHqAdapter)
        mock_client = mock.MagicMock()
        mock_client.connect.return_value = True
        mock_client.login.return_value = True
        adapter._client = mock_client

        result = adapter.connect('1.2.3.4', 7709, time_out=5)
        mock_client.connect.assert_called_once_with(ip='1.2.3.4', port=7709, time_out=5)
        assert result == adapter
        assert adapter._ip == '1.2.3.4'
        assert adapter._port == 7709

    def test_close_opentdx_backend(self):
        adapter = StdHqAdapter.__new__(StdHqAdapter)
        mock_client = mock.MagicMock()
        adapter._client = mock_client
        adapter._connected = True

        adapter.close()
        mock_client.disconnect.assert_called_once()
        assert adapter._connected is False
