"""测试 StdQuotes 其他未覆盖方法"""
from unittest import mock

import pandas as pd
import pytest

from mootdx.quotes import StdQuotes, BaseQuotes, ExtQuotes


@pytest.fixture
def std_mock():
    q = StdQuotes.__new__(StdQuotes)
    mock_adapter = mock.MagicMock()
    mock_adapter._backend = 'opentdx'
    mock_adapter._client = mock.MagicMock()
    q.client = mock_adapter
    q.bestip = ('1.2.3.4', 7709)
    q.server = ('1.2.3.4', 7709)
    q.timeout = 15
    q.verbose = False
    q.client._connected = True
    return q, mock_adapter


class TestStdQuotesMore:
    def test_traffic(self, std_mock):
        q, adapter = std_mock
        adapter.get_traffic_stats.return_value = {'sent': 100, 'received': 200}
        result = q.traffic()
        assert result == {'sent': 100, 'received': 200}

    def test_quotes_no_symbol(self, std_mock):
        q, adapter = std_mock
        result = q.quotes(symbol=None)
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_ohlc_delegates_to_k(self, std_mock):
        q, adapter = std_mock
        adapter.get_security_bars.return_value = [
            {'open': 10, 'high': 12, 'low': 9, 'close': 11, 'amount': 1000, 'vol': 100,
             'year': 2024, 'month': 1, 'day': 15, 'hour': 0, 'minute': 0, 'datetime': '2024-01-15 00:00'}
        ]
        adapter.to_df.return_value = pd.DataFrame({
            'open': [10], 'high': [12], 'low': [9], 'close': [11], 'amount': [1000], 'volume': [100],
            'year': [2024], 'month': [1], 'day': [15], 'hour': [0], 'minute': [0],
            'datetime': ['2024-01-15 00:00']
        })
        result = q.ohlc(symbol='000001', begin='2024-01-01', end='2024-01-31')
        assert isinstance(result, pd.DataFrame)

    def test_block(self, std_mock):
        q, adapter = std_mock
        adapter.get_and_parse_block_info.return_value = [
            {'name': '上海A股', 'code': '880001'},
            {'name': '深圳A股', 'code': '880002'},
        ]
        result = q.block(tofile='block.dat')
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert result.iloc[0]['name'] == '上海A股'
        assert 'code' in result.columns

    def test_finance(self, std_mock):
        q, adapter = std_mock
        adapter.get_finance_info.return_value = {
            'market': 1, 'code': '000001', 'liutongguben': 1000000,
            'province': 1, 'industry': '银行',
        }
        result = q.finance(symbol='000001')
        assert isinstance(result, pd.DataFrame)
        assert result.iloc[0]['code'] == '000001'
        assert result.iloc[0]['market'] == 1

    def test_xdxr(self, std_mock):
        q, adapter = std_mock
        adapter.get_xdxr_info.return_value = [
            {'name': '除权除息', 'year': 2024, 'month': 6, 'day': 15,
             'category': 2, 'fenhong': 0.5, 'songzhuangu': 0.3},
        ]
        result = q.xdxr(symbol='000001')
        assert isinstance(result, pd.DataFrame)
        assert result.iloc[0]['name'] == '除权除息'
        assert result.iloc[0]['category'] == 2

    def test_F10_with_name(self, std_mock):
        q, adapter = std_mock
        adapter.get_company_info_category.return_value = [
            {'name': '公司概况', 'filename': 'f1.txt', 'start': 0, 'length': 100}
        ]
        adapter.get_company_info_content.return_value = {'content': 'data'}
        result = q.F10(symbol='000001', name='公司概况')
        assert result == {'content': 'data'}

    def test_F10_all(self, std_mock):
        q, adapter = std_mock
        adapter.get_company_info_category.return_value = [
            {'name': 'a', 'filename': 'f1.txt', 'start': 0, 'length': 10},
            {'name': 'b', 'filename': 'f2.txt', 'start': 0, 'length': 10},
        ]
        adapter.get_company_info_content.return_value = {'content': 'data'}
        result = q.F10(symbol='000001')
        assert isinstance(result, dict)
        assert 'a' in result
        assert 'b' in result
        assert result['a'] == {'content': 'data'}

    def test_F10C(self, std_mock):
        q, adapter = std_mock
        adapter.get_company_info_category.return_value = [{'name': 'test'}]
        result = q.F10C(symbol='000001')
        assert result == [{'name': 'test'}]

    def test_stocks(self, std_mock):
        q, adapter = std_mock
        adapter.get_security_count.return_value = 3
        adapter.get_security_list.return_value = [
            {'code': '000001', 'volunit': 100, 'decimal_point': 2, 'name': '平安银行', 'pre_close': 10.5},
            {'code': '000002', 'volunit': 100, 'decimal_point': 2, 'name': '万科A', 'pre_close': 15.0},
        ]
        result = q.stocks(market=0)
        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 2
        assert 'code' in result.columns
        assert 'name' in result.columns
        assert result.iloc[0]['code'] == '000001'

    def test_stock_count(self, std_mock):
        q, adapter = std_mock
        adapter.get_security_count.return_value = 5000
        result = q.stock_count(market=0)
        assert result == 5000

    def test_transactions(self, std_mock):
        q, adapter = std_mock
        adapter.get_history_transaction_data.return_value = [
            {'time': '09:30', 'price': 10.5, 'volume': 100, 'num': 1, 'direction': 0},
            {'time': '09:31', 'price': 10.6, 'volume': 200, 'num': 2, 'direction': 1},
        ]
        result = q.transactions(symbol='000001', start=0, offset=10, date='20240101')
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert result.iloc[0]['price'] == 10.5

    def test_index(self, std_mock):
        q, adapter = std_mock
        adapter.get_index_bars.return_value = [
            {'open': 3000, 'high': 3050, 'low': 2990, 'close': 3025, 'amount': 5000000, 'vol': 800000,
             'year': 2024, 'month': 1, 'day': 15, 'hour': 0, 'minute': 0, 'datetime': '2024-01-15 00:00'}
        ]
        result = q.index(symbol='000001', frequency=9, start=0, offset=100)
        assert isinstance(result, pd.DataFrame)
        assert 'open' in result.columns
        assert result.iloc[0]['close'] == 3025

    def test_get_k_data(self, std_mock):
        q, adapter = std_mock
        adapter.get_security_bars.return_value = [
            {'open': 10, 'high': 12, 'low': 9, 'close': 11, 'amount': 1000, 'vol': 100,
             'year': 2024, 'month': 1, 'day': 15, 'hour': 0, 'minute': 0, 'datetime': '2024-01-15 00:00'}
        ]
        adapter.to_df.return_value = pd.DataFrame({
            'open': [10], 'high': [12], 'low': [9], 'close': [11], 'amount': [1000], 'volume': [100],
            'year': [2024], 'month': [1], 'day': [15], 'hour': [0], 'minute': [0],
            'datetime': ['2024-01-15 00:00'], 'date': ['2024-01-15'], 'code': ['000001']
        })
        result = q.get_k_data('000001', '2024-01-01', '2024-01-31')
        assert isinstance(result, pd.DataFrame)
        assert 'open' in result.columns
        assert 'close' in result.columns
        assert not result.empty

    def test_reconnect_when_closed(self, std_mock):
        q, adapter = std_mock
        q.client._connected = False
        q.reconnect()
        adapter.connect.assert_called()

    def test_stock_all(self, std_mock):
        q, adapter = std_mock
        adapter.get_security_count.return_value = 3
        adapter.get_security_list.return_value = [
            {'code': '000001', 'volunit': 100, 'decimal_point': 2, 'name': 'test_sh', 'pre_close': 10},
            {'code': '600001', 'volunit': 100, 'decimal_point': 2, 'name': 'test_sz', 'pre_close': 20},
        ]
        result = q.stock_all()
        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 2
        assert 'code' in result.columns


class TestExtQuotesValidate:
    def test_validate_market_and_symbol(self):
        assert ExtQuotes.validate(47, 'IFL0') == (47, 'IFL0')

    def test_validate_symbol_with_hash(self):
        assert ExtQuotes.validate(None, '47#IFL0') == (47, 'IFL0')

    def test_validate_no_market_raises(self):
        with pytest.raises(ValueError, match='市场参数错误'):
            ExtQuotes.validate(None, 'IFL0')
