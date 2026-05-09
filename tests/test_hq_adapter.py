import datetime
from collections import OrderedDict
from unittest import mock

import pandas as pd
import pytest

from mootdx.hq_adapter import StdHqAdapter


class TestStdHqAdapterInit:
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
        from opentdx import parse_tdx_date
        assert parse_tdx_date(None) is None

    def test_empty_string_returns_none(self):
        from opentdx import parse_tdx_date
        assert parse_tdx_date('') is None

    def test_date_object_passthrough(self):
        from opentdx import parse_tdx_date
        d = datetime.date(2024, 1, 15)
        assert parse_tdx_date(d) == d

    def test_int_yyyymmdd(self):
        from opentdx import parse_tdx_date
        result = parse_tdx_date(20240115)
        assert result == datetime.date(2024, 1, 15)

    def test_int_boundary(self):
        from opentdx import parse_tdx_date
        result = parse_tdx_date(20231231)
        assert result == datetime.date(2023, 12, 31)

    def test_non_date_returns_none(self):
        from opentdx import parse_tdx_date
        assert parse_tdx_date('not-a-date') is None

    def test_zero_int_returns_none(self):
        from opentdx import parse_tdx_date
        assert parse_tdx_date(0) is None

    def test_negative_int_returns_none(self):
        from opentdx import parse_tdx_date
        assert parse_tdx_date(-1) is None


class TestContextManager:
    def test_enter_returns_self(self):
        adapter = StdHqAdapter()
        assert adapter.__enter__() is adapter

    def test_exit_calls_close(self):
        adapter = StdHqAdapter()
        with mock.patch.object(adapter, 'close') as mock_close:
            adapter.__exit__(None, None, None)
            mock_close.assert_called_once()

    def test_close_disconnects_client(self):
        adapter = StdHqAdapter()
        mock_client = mock.MagicMock()
        adapter._client = mock_client
        adapter._connected = True
        adapter.close()
        mock_client.disconnect.assert_called_once()
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
        from opentdx import MARKET
        adapter = StdHqAdapter()
        assert adapter._convert_market(0) == MARKET.SZ
        assert adapter._convert_market(1) == MARKET.SH

    def test_convert_market_fallback(self):
        from opentdx import MARKET
        adapter = StdHqAdapter()
        assert adapter._convert_market(99) == MARKET.SH


class TestConvertPeriod:
    def test_convert_period_normal(self):
        from opentdx import PERIOD
        adapter = StdHqAdapter()
        assert adapter._convert_period(9) == PERIOD.DAYS
        assert adapter._convert_period(4) == PERIOD.DAILY

    def test_convert_period_fallback(self):
        from opentdx import PERIOD
        adapter = StdHqAdapter()
        assert adapter._convert_period(-1) == PERIOD.DAILY
