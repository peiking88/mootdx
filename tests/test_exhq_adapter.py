import datetime
from unittest import mock

import pytest

from mootdx.exhq_adapter import ExHqAdapter


class TestExHqAdapterInit:
    def test_init_defaults(self):
        adapter = ExHqAdapter()
        assert adapter._connected is False
        assert adapter._ip is None
        assert adapter._port is None


class TestParseDate:
    def test_none_returns_none(self):
        from opentdx import parse_tdx_date
        assert parse_tdx_date(None) is None

    def test_empty_string_returns_none(self):
        from opentdx import parse_tdx_date
        assert parse_tdx_date('') is None

    def test_date_object_passthrough(self):
        from opentdx import parse_tdx_date
        d = datetime.date(2024, 6, 1)
        assert parse_tdx_date(d) == d

    def test_int_yyyymmdd(self):
        from opentdx import parse_tdx_date
        result = parse_tdx_date(20240601)
        assert result == datetime.date(2024, 6, 1)

    def test_non_date_string_returns_none(self):
        from opentdx import parse_tdx_date
        assert parse_tdx_date('abc') is None

    def test_zero_int_returns_none(self):
        from opentdx import parse_tdx_date
        assert parse_tdx_date(0) is None


class TestConnectArgs:
    def test_two_args(self):
        adapter = ExHqAdapter()
        adapter._connected = False
        assert adapter._ip is None
        assert adapter._port is None

    def test_three_args_parsing(self):
        """connect(name, ip, port) 应正确解析三个参数"""
        adapter = ExHqAdapter()
        with mock.patch.object(adapter, '_client') as mock_client:
            mock_client.login.return_value = True
            mock_client.connect.return_value = True
            adapter._backend = 'opentdx'
            adapter.connect('site_name', '1.2.3.4', 7727)
            assert adapter._ip == '1.2.3.4'
            assert adapter._port == 7727

    def test_two_args_parsing(self):
        adapter = ExHqAdapter()
        with mock.patch.object(adapter, '_client') as mock_client:
            mock_client.login.return_value = True
            mock_client.connect.return_value = True
            adapter._backend = 'opentdx'
            adapter.connect('1.2.3.4', 7727)
            assert adapter._ip == '1.2.3.4'
            assert adapter._port == 7727

    def test_invalid_args_count(self):
        adapter = ExHqAdapter()
        with pytest.raises(ValueError, match='Expected'):
            adapter.connect('a', 'b', 'c', 'd')


class TestContextManager:
    def test_enter_returns_self(self):
        adapter = ExHqAdapter()
        assert adapter.__enter__() is adapter

    def test_exit_calls_close(self):
        adapter = ExHqAdapter()
        with mock.patch.object(adapter, 'close') as mock_close:
            adapter.__exit__(None, None, None)
            mock_close.assert_called_once()

    def test_close_sets_connected_flag(self):
        adapter = ExHqAdapter()
        adapter._connected = True
        adapter.close()
        assert adapter._connected is False
