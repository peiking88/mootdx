import json
import socket
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from mootdx import server as server_module
from mootdx.server import bestip, connect, server, hosts, results


class TestServerFunction:
    def test_server_sync_mode(self):
        with mock.patch('mootdx.server.connect') as mock_connect:
            mock_connect.return_value = {'addr': '1.2.3.4', 'port': 7709, 'time': 10.0, 'site': 'test'}
            test_hosts = [{'addr': '1.2.3.4', 'port': 7709, 'time': 0, 'site': 'test'}]
            with mock.patch.dict('mootdx.server.hosts', {'HQ': test_hosts}):
                with mock.patch.dict('mootdx.server.results', {'HQ': []}):
                    result = server(index='HQ', limit=5, console=False, sync=True)
                    assert len(result) == 1
                    assert result[0] == ('1.2.3.4', 7709)

    def test_server_with_console(self):
        with mock.patch('mootdx.server.connect') as mock_connect:
            mock_connect.return_value = {'addr': '1.2.3.4', 'port': 7709, 'time': 5.0, 'site': 'test'}
            test_hosts = [{'addr': '1.2.3.4', 'port': 7709, 'time': 0, 'site': 'test'}]
            with mock.patch.dict('mootdx.server.hosts', {'HQ': test_hosts}):
                with mock.patch.dict('mootdx.server.results', {'HQ': []}):
                    result = server(index='HQ', limit=5, console=True, sync=True)
                    assert result[0] == ('1.2.3.4', 7709)

    def test_server_sync_empty_result(self):
        with mock.patch('mootdx.server.connect') as mock_connect:
            mock_connect.return_value = {'addr': '1.2.3.4', 'port': 7709, 'time': None, 'site': 'test'}
            test_hosts = [{'addr': '1.2.3.4', 'port': 7709, 'time': 0, 'site': 'test'}]
            with mock.patch.dict('mootdx.server.hosts', {'HQ': test_hosts}):
                with mock.patch.dict('mootdx.server.results', {'HQ': []}):
                    result = server(index='HQ', limit=5, console=False, sync=True)
                    # time=None results are filtered out
                    assert len(result) == 0


class TestBestip:
    def test_bestip_writes_config(self, tmp_path):
        config_path = tmp_path / 'config.json'

        mock_hq = [{'addr': '10.0.0.1', 'port': 7709, 'time': 5.0, 'site': 'test'}]
        with mock.patch('mootdx.server.server') as mock_server:
            mock_server.side_effect = lambda **kw: ([('10.0.0.1', 7709)] if kw['index'] != 'GP' else [])
            with mock.patch('mootdx.server.get_config_path', return_value=str(config_path)):
                bestip(console=False, limit=5, sync=True)

        assert config_path.exists()
        data = json.load(open(config_path))
        assert 'BESTIP' in data
        assert 'SERVER' in data

    def test_bestip_runtime_error(self, tmp_path):
        config_path = tmp_path / 'config.json'

        with mock.patch('mootdx.server.server') as mock_server:
            mock_server.side_effect = RuntimeError('event loop')
            with mock.patch('mootdx.server.get_config_path', return_value=str(config_path)):
                bestip(console=False, limit=5, sync=True)

        # RuntimeError 被捕获后应写入默认配置
        assert config_path.exists()
        data = json.load(open(config_path))
        assert 'SERVER' in data
        assert 'BESTIP' in data

