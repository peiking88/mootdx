import socket
from unittest import mock

import pandas as pd
import pytest

from mootdx.quotes import BaseQuotes, Quotes, check_empty, valid_server


class TestValidServer:
    def test_tuple(self):
        result = valid_server(('1.2.3.4', 7709))
        assert result == ('1.2.3.4', 7709)

    def test_list(self):
        result = valid_server(['10.0.0.1', 7709])
        assert result == ('10.0.0.1', 7709)

    def test_port_as_string(self):
        result = valid_server(['192.168.1.1', '7727'])
        assert result == ('192.168.1.1', 7727)

    def test_invalid_ip_raises(self):
        with pytest.raises(ValueError, match='Server'):
            valid_server(['not-an-ip', 7709])

    def test_none_returns_none(self):
        assert valid_server(None) is None

    def test_non_tuple_list(self):
        assert valid_server('string') is None

    def test_empty_list(self):
        with pytest.raises(ValueError):
            valid_server([])


class TestCheckEmpty:
    def setup_method(self):
        import mootdx.quotes as mq
        mq.instance = None

    def test_empty_dataframe(self):
        import mootdx.quotes as mq
        mq.instance = None
        df = pd.DataFrame()
        assert check_empty(df) is True

    def test_non_empty_dataframe(self):
        import mootdx.quotes as mq
        mq.instance = None
        df = pd.DataFrame({'a': [1, 2]})
        assert check_empty(df) is False

    def test_empty_list(self):
        import mootdx.quotes as mq
        mq.instance = None
        assert check_empty([]) is True

    def test_non_empty_list(self):
        import mootdx.quotes as mq
        mq.instance = None
        assert check_empty([1, 2]) is False

    def test_none(self):
        import mootdx.quotes as mq
        mq.instance = None
        assert check_empty(None) is True

    def test_zero_is_falsey(self):
        import mootdx.quotes as mq
        mq.instance = None
        assert check_empty(0) is True


class TestBaseQuotes:
    def test_close_no_client(self):
        with mock.patch('mootdx.quotes.config.setup'):
            obj = BaseQuotes.__new__(BaseQuotes)
            obj.client = None
            obj.close()

    def test_close_with_client(self):
        with mock.patch('mootdx.quotes.config.setup'):
            obj = BaseQuotes.__new__(BaseQuotes)
            mock_client = mock.MagicMock()
            obj.client = mock_client
            obj.close()
            mock_client.close.assert_called_once()

    def test_closed_with_connected_attr(self):
        with mock.patch('mootdx.quotes.config.setup'):
            obj = BaseQuotes.__new__(BaseQuotes)
            mock_client = mock.MagicMock()
            mock_client._connected = True
            obj.client = mock_client
            assert obj.closed is False

    def test_closed_with_connected_false(self):
        with mock.patch('mootdx.quotes.config.setup'):
            obj = BaseQuotes.__new__(BaseQuotes)
            mock_client = mock.MagicMock()
            mock_client._connected = False
            obj.client = mock_client
            assert obj.closed is True

    def test_closed_no_client(self):
        with mock.patch('mootdx.quotes.config.setup'):
            obj = BaseQuotes.__new__(BaseQuotes)
            obj.client = None
            assert obj.closed is True
