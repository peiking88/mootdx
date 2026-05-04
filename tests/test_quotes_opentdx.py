"""测试 StdQuotes 中依赖 opentdx 的方法"""
from unittest import mock

import pandas as pd
import pytest

import mootdx.quotes


def make_std_mock():
    """创建一个使用 opentdx 后端的 StdQuotes 实例"""
    from mootdx.quotes import StdQuotes

    q = StdQuotes.__new__(StdQuotes)
    mock_adapter = mock.MagicMock()
    mock_adapter._backend = 'opentdx'
    mock_adapter._connected = True
    mock_adapter._client = mock.MagicMock()
    q.client = mock_adapter
    q.bestip = ('1.2.3.4', 7709)
    q.server = ('1.2.3.4', 7709)
    return q, mock_adapter


class TestRequireOpentdx:
    def test_opentdx_backend_ok(self):
        q, _ = make_std_mock()
        q._require_opentdx()

    def test_tdxpy_backend_raises(self):
        q, adapter = make_std_mock()
        adapter._backend = 'tdxpy'
        with pytest.raises(NotImplementedError, match='opentdx'):
            q._require_opentdx()


class TestOpentdxMethods:
    def test_stock_ranking_ok(self):
        q, adapter = make_std_mock()
        mock_otdx = adapter._client
        mock_cat = mock.MagicMock()
        mock_cat.A = 1
        mock_otdx.get_stock_top_board.return_value = {'rank': []}

        with mock.patch.dict('sys.modules', {'opentdx': mock.MagicMock(CATEGORY=mock_cat)}):
            result = q.stock_ranking()
            mock_otdx.get_stock_top_board.assert_called_once()

    def test_stock_list_sorted_ok(self):
        q, adapter = make_std_mock()
        mock_otdx = adapter._client
        mock_cat = mock.MagicMock()
        mock_cat.A = 2
        mock_sort = mock.MagicMock()
        mock_sort.CHANGE_PCT = 1
        mock_otdx.get_stock_quotes_list.return_value = [{'code': '000001'}]

        with mock.patch.dict('sys.modules', {
            'opentdx': mock.MagicMock(CATEGORY=mock_cat, SORT_TYPE=mock_sort),
        }):
            result = q.stock_list_sorted(count=80)
            mock_otdx.get_stock_quotes_list.assert_called_once()

    def test_board_list_ok(self):
        q, adapter = make_std_mock()
        mock_bt = mock.MagicMock()
        mock_bt.HY = 1
        mock_sp = mock.MagicMock()
        mock_sp.get_board_list.return_value = [{'code': '880001'}]
        q._get_sp_client = mock.MagicMock(return_value=mock_sp)

        with mock.patch.dict('sys.modules', {'opentdx': mock.MagicMock(BOARD_TYPE=mock_bt)}):
            result = q.board_list(board_type='industry')
            mock_sp.get_board_list.assert_called_once()

    def test_board_quotes_ok(self):
        q, adapter = make_std_mock()
        mock_sort_t = mock.MagicMock()
        mock_sort_t.CHANGE_PCT = 1
        mock_sp = mock.MagicMock()
        mock_sp.get_board_members_quotes.return_value = [{'code': '000001'}]
        q._get_sp_client = mock.MagicMock(return_value=mock_sp)

        with mock.patch.dict('sys.modules', {
            'opentdx': mock.MagicMock(SORT_TYPE=mock_sort_t),
        }):
            result = q.board_quotes('880001')
            mock_sp.get_board_members_quotes.assert_called_once()

    def test_capital_flow_ok(self):
        q, adapter = make_std_mock()
        mock_mkt = mock.MagicMock()
        mock_sp = mock.MagicMock()
        mock_sp.get_symbol_zjlx.return_value = {'inflow': 100}
        q._get_sp_client = mock.MagicMock(return_value=mock_sp)

        with mock.patch.dict('sys.modules', {'opentdx': mock.MagicMock(MARKET=mock_mkt)}):
            result = q.capital_flow('000001')
            mock_sp.get_symbol_zjlx.assert_called_once()

    def test_auction_ok(self):
        q, adapter = make_std_mock()
        mock_otdx = adapter._client
        mock_mkt = mock.MagicMock()
        mock_otdx.get_auction.return_value = [{'price': 10}]

        with mock.patch.dict('sys.modules', {'opentdx': mock.MagicMock(MARKET=mock_mkt)}):
            result = q.auction('000001')
            mock_otdx.get_auction.assert_called_once()

    def test_unusual_ok(self):
        q, adapter = make_std_mock()
        mock_otdx = adapter._client
        mock_mkt = mock.MagicMock()
        mock_otdx.get_unusual.return_value = [{'type': 'surge'}]

        with mock.patch.dict('sys.modules', {'opentdx': mock.MagicMock(MARKET=mock_mkt)}):
            result = q.unusual(market=0)
            mock_otdx.get_unusual.assert_called_once()

    def test_vol_profile_ok(self):
        q, adapter = make_std_mock()
        mock_otdx = adapter._client
        mock_mkt = mock.MagicMock()
        mock_otdx.get_vol_profile.return_value = [{'price': 10}]

        with mock.patch.dict('sys.modules', {'opentdx': mock.MagicMock(MARKET=mock_mkt)}):
            result = q.vol_profile('000001')
            mock_otdx.get_vol_profile.assert_called_once()

    def test_index_info_ok(self):
        q, adapter = make_std_mock()
        mock_otdx = adapter._client
        mock_mkt = mock.MagicMock()
        mock_otdx.get_index_info.return_value = [{'code': '000001'}]

        with mock.patch.dict('sys.modules', {'opentdx': mock.MagicMock(MARKET=mock_mkt)}):
            result = q.index_info(['000001'])
            mock_otdx.get_index_info.assert_called_once()

    def test_get_sp_client_cached(self):
        q, adapter = make_std_mock()
        mock_sp = mock.MagicMock()
        q._get_sp_client = mock.MagicMock(return_value=mock_sp)
        sp1 = q._get_sp_client()
        sp2 = q._get_sp_client()
        assert sp1 is sp2
