import configparser
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from mootdx.tdxfinder import find_tdx_dir, parse_connect_cfg, update_servers_from_tdx, TDX_SEARCH_PATHS


class TestFindTdxDir:
    def test_found_in_first_path(self, tmp_path):
        tdx_dir = tmp_path / 'tdx'
        tdx_dir.mkdir()
        (tdx_dir / 'connect.cfg').write_text('')

        with mock.patch('mootdx.tdxfinder.TDX_SEARCH_PATHS', [tdx_dir]):
            result = find_tdx_dir()
            assert result == tdx_dir

    def test_found_in_second_path(self, tmp_path):
        dir1 = tmp_path / 'no_cfg'
        dir1.mkdir()
        dir2 = tmp_path / 'has_cfg'
        dir2.mkdir()
        (dir2 / 'connect.cfg').write_text('')

        with mock.patch('mootdx.tdxfinder.TDX_SEARCH_PATHS', [dir1, dir2]):
            result = find_tdx_dir()
            assert result == dir2

    def test_not_found(self, tmp_path):
        dir1 = tmp_path / 'empty'
        dir1.mkdir()

        with mock.patch('mootdx.tdxfinder.TDX_SEARCH_PATHS', [dir1]):
            result = find_tdx_dir()
            assert result is None

    def test_default_paths(self):
        assert len(TDX_SEARCH_PATHS) == 3


class TestParseConnectCfg:
    def make_cfg(self, path):
        cp = configparser.ConfigParser()
        cp['HQHOST'] = {
            'HostName01': 'test_hq',
            'IPAddress01': '10.0.0.1',
            'Port01': '7709',
            'HostName02': 'test_hq2',
            'IPAddress02': '10.0.0.2',
            'Port02': '7710',
        }
        cp['DSHOST'] = {
            'HostName01': 'test_ex',
            'IPAddress01': '10.0.0.3',
            'Port01': '7727',
        }
        cp['HFHost'] = {
            'HostName01': 'test_hf',
            'IPAddress01': '10.0.0.4',
            'Port01': '7709',
        }
        with open(path, 'w', encoding='gbk') as f:
            cp.write(f)
        return path

    def test_parse_valid_cfg(self, tmp_path):
        cfg_path = self.make_cfg(tmp_path / 'connect.cfg')
        result = parse_connect_cfg(cfg_path)
        assert 'HQ' in result
        assert 'EX' in result
        assert 'HF' in result
        assert len(result['HQ']) == 2
        assert result['HQ'][0] == ('test_hq', '10.0.0.1', 7709)
        assert result['HQ'][1] == ('test_hq2', '10.0.0.2', 7710)
        assert result['EX'][0] == ('test_ex', '10.0.0.3', 7727)
        assert result['HF'][0] == ('test_hf', '10.0.0.4', 7709)

    def test_parse_file_not_exists(self):
        result = parse_connect_cfg('/nonexistent/path/connect.cfg')
        assert result is None

    def test_parse_none_path_no_tdx(self):
        with mock.patch('mootdx.tdxfinder.find_tdx_dir', return_value=None):
            result = parse_connect_cfg()
            assert result is None

    def test_parse_none_path_with_tdx(self, tmp_path):
        tdx_dir = tmp_path / 'tdx'
        tdx_dir.mkdir()
        self.make_cfg(tdx_dir / 'connect.cfg')

        with mock.patch('mootdx.tdxfinder.find_tdx_dir', return_value=tdx_dir):
            result = parse_connect_cfg()
            assert 'HQ' in result

    def test_default_port(self, tmp_path):
        cfg_path = tmp_path / 'connect.cfg'
        cp = configparser.ConfigParser()
        cp['HQHOST'] = {
            'HostName01': 'no_port',
            'IPAddress01': '10.0.0.1',
        }
        with open(cfg_path, 'w', encoding='gbk') as f:
            cp.write(f)

        result = parse_connect_cfg(cfg_path)
        assert result['HQ'][0][2] == 7709

    def test_empty_section_skipped(self, tmp_path):
        cfg_path = tmp_path / 'connect.cfg'
        cp = configparser.ConfigParser()
        cp['HQHOST'] = {}
        with open(cfg_path, 'w', encoding='gbk') as f:
            cp.write(f)

        result = parse_connect_cfg(cfg_path)
        assert 'HQ' not in result


class TestUpdateServersFromTdx:
    def test_no_tdx_config(self):
        with mock.patch('mootdx.tdxfinder.parse_connect_cfg', return_value=None):
            result = update_servers_from_tdx()
            assert result is False

    def test_update_hq_and_ex(self):
        servers = {
            'HQ': [('h1', '10.0.0.1', 7709), ('h2', '10.0.0.2', 7709)],
            'EX': [('e1', '10.0.0.3', 7727)],
        }
        with mock.patch('mootdx.tdxfinder.parse_connect_cfg', return_value=servers):
            from mootdx import config
            current_hq = config.get('SERVER').get('HQ')
            current_ex = config.get('SERVER').get('EX')
            # 确保触发变更
            with mock.patch.object(config, 'settings', {
                'SERVER': {'HQ': [('old', '0.0.0.0', 1)], 'EX': [('old', '0.0.0.0', 1)]},
                'BESTIP': {'HQ': '', 'EX': '', 'GP': ''},
                'TDXDIR': '',
            }):
                result = update_servers_from_tdx()
                assert result is True

    def test_no_change_when_same(self):
        servers = {'HQ': [('same', '1.1.1.1', 7709)]}
        with mock.patch('mootdx.tdxfinder.parse_connect_cfg', return_value=servers):
            with mock.patch('mootdx.config.settings', {
                'SERVER': {'HQ': [('same', '1.1.1.1', 7709)], 'EX': [], 'GP': []},
                'BESTIP': {'HQ': '', 'EX': '', 'GP': ''},
                'TDXDIR': '',
            }):
                result = update_servers_from_tdx()
                assert result is False

    def test_hf_added(self):
        servers = {'HF': [('hf1', '10.0.0.5', 7709)]}
        with mock.patch('mootdx.tdxfinder.parse_connect_cfg', return_value=servers):
            with mock.patch('mootdx.config.settings', {
                'SERVER': {'HQ': [], 'EX': [], 'GP': []},
                'BESTIP': {'HQ': '', 'EX': '', 'GP': ''},
                'TDXDIR': '',
            }):
                result = update_servers_from_tdx()
                assert result is True
