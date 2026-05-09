import socket
import time
from unittest import mock

from mootdx.server import bestip, connect, hosts


class TestServerHosts:
    def test_hosts_structure(self):
        assert 'HQ' in hosts
        assert 'EX' in hosts
        assert 'GP' in hosts
        for key in hosts:
            assert isinstance(hosts[key], list)
            if hosts[key]:
                item = hosts[key][0]
                assert 'addr' in item
                assert 'port' in item
                assert 'time' in item
                assert 'site' in item


class TestConnect:
    def test_connect_success(self):
        with mock.patch('socket.socket') as mock_socket_class:
            mock_sock = mock.MagicMock()
            mock_socket_class.return_value = mock_sock
            mock_sock.settimeout = mock.MagicMock()

            result = connect({'addr': '1.2.3.4', 'port': 7709})
            assert result['time'] is not None
            assert isinstance(result['time'], float)

    def test_connect_refused(self):
        with mock.patch('socket.socket') as mock_socket_class:
            mock_sock = mock.MagicMock()
            mock_socket_class.return_value = mock_sock
            mock_sock.connect.side_effect = ConnectionRefusedError()

            result = connect({'addr': '1.2.3.4', 'port': 7709})
            assert result['time'] is None

    def test_connect_timeout(self):
        with mock.patch('socket.socket') as mock_socket_class:
            mock_sock = mock.MagicMock()
            mock_socket_class.return_value = mock_sock
            mock_sock.connect.side_effect = socket.timeout()

            result = connect({'addr': '1.2.3.4', 'port': 7709})
            assert result['time'] is None

    def test_connect_oserror(self):
        with mock.patch('socket.socket') as mock_socket_class:
            mock_sock = mock.MagicMock()
            mock_socket_class.return_value = mock_sock
            mock_sock.connect.side_effect = OSError('Network unreachable')

            result = connect({'addr': '1.2.3.4', 'port': 7709})
            assert result['time'] is None


