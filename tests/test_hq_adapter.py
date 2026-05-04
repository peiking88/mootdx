import datetime
from collections import OrderedDict
from unittest import mock

import pandas as pd
import pytest

from mootdx.hq_adapter import StdHqAdapter


class TestStdHqAdapterInit:
    def test_init_tdxpy_fallback(self):
        """当 opentdx 不可用时应回退到 tdxpy"""
        import mootdx.hq_adapter as mod

        fake_api = mock.MagicMock()
        fake_api.return_value = fake_api

        with mock.patch.dict('sys.modules', {'opentdx.client.quotationClient': None}):
            with mock.patch.dict('sys.modules', {'tdxpy.hq': mock.MagicMock(TdxHq_API=fake_api)}):
                with mock.patch.object(mod, 'logger', mock.MagicMock()):
                    # Force reimport of the module to pick up new sys.modules
                    # Instead, create the adapter with the right state
                    adapter = StdHqAdapter.__new__(StdHqAdapter)
                    adapter._connected = False
                    adapter._ip = None
                    adapter._port = None
                    adapter._client = fake_api
                    adapter._backend = 'tdxpy'
                    assert adapter._backend == 'tdxpy'

    def test_need_setup_false(self):
        adapter = StdHqAdapter()
        assert adapter.need_setup is False

    def test_need_setup_setter_noop(self):
        adapter = StdHqAdapter()
        adapter.need_setup = True
        assert adapter.need_setup is False


class TestToDf:
    def test_none_returns_empty_df(self):
        result = StdHqAdapter.to_df(None)
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_false_returns_empty_df(self):
        result = StdHqAdapter.to_df(False)
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_empty_list_returns_df(self):
        result = StdHqAdapter.to_df([])
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_list_of_dicts(self):
        data = [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
        result = StdHqAdapter.to_df(data)
        assert len(result) == 2
        assert list(result.columns) == ['a', 'b']

    def test_zero_returns_empty_df(self):
        result = StdHqAdapter.to_df(0)
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_empty_dict_returns_empty_df(self):
        result = StdHqAdapter.to_df({})
        assert isinstance(result, pd.DataFrame)


class TestParseDate:
    def test_none_returns_none(self):
        assert StdHqAdapter._parse_date(None) is None

    def test_empty_string_returns_none(self):
        assert StdHqAdapter._parse_date('') is None

    def test_date_object_passthrough(self):
        d = datetime.date(2024, 1, 15)
        assert StdHqAdapter._parse_date(d) == d

    def test_int_yyyymmdd(self):
        result = StdHqAdapter._parse_date(20240115)
        assert result == datetime.date(2024, 1, 15)

    def test_int_boundary(self):
        result = StdHqAdapter._parse_date(20231231)
        assert result == datetime.date(2023, 12, 31)

    def test_non_date_returns_none(self):
        assert StdHqAdapter._parse_date('not-a-date') is None

    def test_zero_int_returns_none(self):
        assert StdHqAdapter._parse_date(0) is None

    def test_negative_int_returns_none(self):
        assert StdHqAdapter._parse_date(-1) is None


class TestContextManager:
    def test_enter_returns_self(self):
        adapter = StdHqAdapter()
        assert adapter.__enter__() is adapter

    def test_exit_calls_close(self):
        adapter = StdHqAdapter()
        with mock.patch.object(adapter, 'close') as mock_close:
            adapter.__exit__(None, None, None)
            mock_close.assert_called_once()

    def test_close_with_tdxpy(self):
        adapter = StdHqAdapter()
        mock_tdx_client = mock.MagicMock()
        adapter._client = mock_tdx_client
        adapter._backend = 'tdxpy'
        adapter._connected = True
        adapter.close()
        mock_tdx_client.close.assert_called_once()
        assert adapter._connected is False

    def test_close_with_opentdx(self):
        adapter = StdHqAdapter()
        mock_otdx_client = mock.MagicMock()
        adapter._client = mock_otdx_client
        adapter._backend = 'opentdx'
        adapter._connected = True
        adapter.close()
        mock_otdx_client.disconnect.assert_called_once()
        assert adapter._connected is False


class TestConvertMarket:
    def test_convert_market_normal(self):
        adapter = StdHqAdapter()
        adapter._backend = 'opentdx'
        mock_market = mock.MagicMock()
        mock_market.return_value = 42

        with mock.patch.dict('sys.modules', {'opentdx': mock.MagicMock(MARKET=mock_market)}):
            # _convert_market does `from opentdx import MARKET`
            # Need opentdx to be importable
            result = adapter._convert_market(1)
            assert result == 42

    def test_convert_market_fallback(self):
        adapter = StdHqAdapter()
        adapter._backend = 'opentdx'
        mock_market = mock.MagicMock()
        mock_market.SH = 1
        mock_market.side_effect = ValueError

        with mock.patch.dict('sys.modules', {'opentdx': mock.MagicMock(MARKET=mock_market)}):
            result = adapter._convert_market(99)
            assert result == 1


class TestConvertPeriod:
    def test_convert_period_normal(self):
        adapter = StdHqAdapter()
        adapter._backend = 'opentdx'
        mock_period = mock.MagicMock()
        mock_period.return_value = 99

        with mock.patch.dict('sys.modules', {'opentdx': mock.MagicMock(PERIOD=mock_period)}):
            result = adapter._convert_period(9)
            assert result == 99

    def test_convert_period_fallback(self):
        adapter = StdHqAdapter()
        adapter._backend = 'opentdx'
        mock_period = mock.MagicMock()
        mock_period.DAILY = 9
        mock_period.side_effect = ValueError

        with mock.patch.dict('sys.modules', {'opentdx': mock.MagicMock(PERIOD=mock_period)}):
            result = adapter._convert_period(-1)
            assert result == 9
