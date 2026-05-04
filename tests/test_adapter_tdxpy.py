"""测试适配器在 tdxpy 后端下的方法委托"""
from collections import OrderedDict
from unittest import mock

import pytest

from mootdx.hq_adapter import StdHqAdapter
from mootdx.exhq_adapter import ExHqAdapter


def make_tdxpy_adapter():
    """创建使用 tdxpy 后端的 StdHqAdapter"""
    adapter = StdHqAdapter.__new__(StdHqAdapter)
    mock_tdx = mock.MagicMock()
    adapter._client = mock_tdx
    adapter._backend = 'tdxpy'
    adapter._connected = True
    adapter._ip = '1.2.3.4'
    adapter._port = 7709
    return adapter, mock_tdx


def make_tdxpy_exhq():
    adapter = ExHqAdapter.__new__(ExHqAdapter)
    mock_tdx = mock.MagicMock()
    adapter._client = mock_tdx
    adapter._backend = 'tdxpy'
    adapter._connected = True
    adapter._ip = '1.2.3.4'
    adapter._port = 7727
    return adapter, mock_tdx


class TestStdHqTdxpyDelegation:
    def _adapter(self):
        return make_tdxpy_adapter()

    def test_get_security_bars(self):
        ad, cl = self._adapter()
        cl.get_security_bars.return_value = [{'open': 10}]
        result = ad.get_security_bars(9, 0, '000001', 0, 100)
        cl.get_security_bars.assert_called_once_with(9, 0, '000001', 0, 100)
        assert result == [{'open': 10}]

    def test_get_index_bars(self):
        ad, cl = self._adapter()
        cl.get_index_bars.return_value = [{'open': 11}]
        result = ad.get_index_bars(9, 1, '000001', 0, 100)
        cl.get_index_bars.assert_called_once_with(9, 1, '000001', 0, 100)

    def test_get_security_quotes(self):
        ad, cl = self._adapter()
        cl.get_security_quotes.return_value = [{'price': 10}]
        result = ad.get_security_quotes([(0, '000001')])
        cl.get_security_quotes.assert_called_once()

    def test_get_security_count(self):
        ad, cl = self._adapter()
        cl.get_security_count.return_value = 5000
        result = ad.get_security_count(0)
        assert result == 5000

    def test_get_security_list(self):
        ad, cl = self._adapter()
        cl.get_security_list.return_value = [{'code': '000001'}]
        result = ad.get_security_list(0, 0)
        cl.get_security_list.assert_called_once_with(0, 0)

    def test_get_history_minute_time_data(self):
        ad, cl = self._adapter()
        cl.get_history_minute_time_data.return_value = [{'price': 10}]
        result = ad.get_history_minute_time_data(0, '000001', 20240101)
        cl.get_history_minute_time_data.assert_called_once_with(0, '000001', 20240101)

    def test_get_transaction_data(self):
        ad, cl = self._adapter()
        cl.get_transaction_data.return_value = [{'price': 10}]
        result = ad.get_transaction_data(0, '000001', 0, 100)
        cl.get_transaction_data.assert_called_once_with(0, '000001', 0, 100)

    def test_get_history_transaction_data(self):
        ad, cl = self._adapter()
        cl.get_history_transaction_data.return_value = [{'price': 10}]
        result = ad.get_history_transaction_data(0, '000001', 0, 100, 20240101)
        cl.get_history_transaction_data.assert_called_once_with(0, '000001', 0, 100, 20240101)

    def test_get_xdxr_info(self):
        ad, cl = self._adapter()
        cl.get_xdxr_info.return_value = [{'name': '除权除息'}]
        result = ad.get_xdxr_info(0, '000001')
        cl.get_xdxr_info.assert_called_once_with(0, '000001')

    def test_get_finance_info(self):
        ad, cl = self._adapter()
        cl.get_finance_info.return_value = OrderedDict([('code', '000001')])
        result = ad.get_finance_info(0, '000001')
        cl.get_finance_info.assert_called_once_with(0, '000001')

    def test_get_company_info_category(self):
        ad, cl = self._adapter()
        cl.get_company_info_category.return_value = [{'name': 'test'}]
        result = ad.get_company_info_category(0, '000001')
        cl.get_company_info_category.assert_called_once_with(0, '000001')

    def test_get_company_info_content(self):
        ad, cl = self._adapter()
        cl.get_company_info_content.return_value = {'content': 'data'}
        result = ad.get_company_info_content(0, '000001', 'file.txt', 0, 100)
        cl.get_company_info_content.assert_called_once_with(
            market=0, code='000001', filename='file.txt', start=0, length=100
        )

    def test_get_and_parse_block_info(self):
        ad, cl = self._adapter()
        cl.get_and_parse_block_info.return_value = [{'name': 'block'}]
        result = ad.get_and_parse_block_info('block.dat')
        cl.get_and_parse_block_info.assert_called_once_with('block.dat')

    def test_get_traffic_stats(self):
        ad, cl = self._adapter()
        cl.get_traffic_stats.return_value = {'sent': 100}
        result = ad.get_traffic_stats()
        assert result == {'sent': 100}

    def test_get_report_file_by_size(self):
        ad, cl = self._adapter()
        cl.get_report_file_by_size.return_value = True
        result = ad.get_report_file_by_size('report.dat', 1024, None)
        cl.get_report_file_by_size.assert_called_once_with('report.dat', 1024, None)


class TestExHqTdxpyDelegation:
    def _adapter(self):
        return make_tdxpy_exhq()

    def test_get_markets(self):
        ad, cl = self._adapter()
        cl.get_markets.return_value = [{'market': 47, 'name': 'IF'}]
        result = ad.get_markets()
        cl.get_markets.assert_called_once()

    def test_get_instrument_count(self):
        ad, cl = self._adapter()
        cl.get_instrument_count.return_value = 500
        result = ad.get_instrument_count()
        assert result == 500

    def test_get_instrument_info(self):
        ad, cl = self._adapter()
        cl.get_instrument_info.return_value = [{'code': 'IFL0'}]
        result = ad.get_instrument_info(0, 100)
        cl.get_instrument_info.assert_called_once_with(0, 100)

    def test_get_instrument_quote(self):
        ad, cl = self._adapter()
        cl.get_instrument_quote.return_value = [{'price': 5000}]
        result = ad.get_instrument_quote(47, 'IFL0')
        cl.get_instrument_quote.assert_called_once_with(47, 'IFL0')

    def test_get_instrument_bars(self):
        ad, cl = self._adapter()
        cl.get_instrument_bars.return_value = [{'open': 5000}]
        result = ad.get_instrument_bars(9, 47, 'IFL0', 0, 100)
        cl.get_instrument_bars.assert_called_once_with(9, 47, 'IFL0', 0, 100)

    def test_get_minute_time_data(self):
        ad, cl = self._adapter()
        cl.get_minute_time_data.return_value = [{'price': 5000}]
        result = ad.get_minute_time_data(47, 'IFL0')
        cl.get_minute_time_data.assert_called_once_with(47, 'IFL0')

    def test_get_history_minute_time_data(self):
        ad, cl = self._adapter()
        cl.get_history_minute_time_data.return_value = [{'price': 5000}]
        result = ad.get_history_minute_time_data(47, 'IFL0', 20240101)
        cl.get_history_minute_time_data.assert_called_once_with(47, 'IFL0', 20240101)

    def test_get_transaction_data(self):
        ad, cl = self._adapter()
        cl.get_transaction_data.return_value = [{'price': 5000}]
        result = ad.get_transaction_data(47, 'IFL0', 0, 100)
        cl.get_transaction_data.assert_called_once_with(47, 'IFL0', 0, 100)

    def test_get_history_transaction_data(self):
        ad, cl = self._adapter()
        cl.get_history_transaction_data.return_value = [{'price': 5000}]
        result = ad.get_history_transaction_data(47, 'IFL0', 20240101, 0, 100)
        cl.get_history_transaction_data.assert_called_once_with(47, 'IFL0', 20240101, 0, 100)


class TestExHqConnectTdxpy:
    def test_connect_tdxpy_backend(self):
        adapter = ExHqAdapter.__new__(ExHqAdapter)
        mock_tdx = mock.MagicMock()
        mock_tdx.connect.return_value = mock_tdx
        adapter._client = mock_tdx
        adapter._backend = 'tdxpy'

        result = adapter.connect('1.2.3.4', 7727, time_out=5)
        mock_tdx.connect.assert_called_once_with('1.2.3.4', 7727, time_out=5)
        assert result == mock_tdx
        assert adapter._ip == '1.2.3.4'
        assert adapter._port == 7727

    def test_close_tdxpy_backend(self):
        adapter = ExHqAdapter.__new__(ExHqAdapter)
        mock_tdx = mock.MagicMock()
        adapter._client = mock_tdx
        adapter._backend = 'tdxpy'
        adapter._connected = True

        adapter.close()
        mock_tdx.close.assert_called_once()
        assert adapter._connected is False

    def test_close_opentdx_backend(self):
        adapter = ExHqAdapter.__new__(ExHqAdapter)
        mock_otdx = mock.MagicMock()
        adapter._client = mock_otdx
        adapter._backend = 'opentdx'
        adapter._connected = True

        adapter.close()
        mock_otdx.disconnect.assert_called_once()
        assert adapter._connected is False
