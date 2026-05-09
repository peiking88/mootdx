"""测试 config.setup() 和 path()"""
import json
import tempfile
from pathlib import Path
from unittest import mock

from mootdx import config
from mootdx.consts import HQ_HOSTS, EX_HOSTS, GP_HOSTS


class TestConfigSetup:
    def test_setup_loads_existing_config(self, tmp_path):
        config_file = tmp_path / 'config.json'
        data = {'SERVER': {'HQ': [], 'EX': [], 'GP': []}, 'BESTIP': {'HQ': '', 'EX': '', 'GP': ''}, 'TDXDIR': '/test'}
        config_file.write_text(json.dumps(data))

        with mock.patch('mootdx.config.CONF', str(config_file)):
            config.setup()
            assert config.settings.get('TDXDIR') == '/test'

    def test_setup_with_existing_config_no_bestip(self, tmp_path):
        config_file = tmp_path / 'missing.json'
        write_data = {'SERVER': {'HQ': [], 'EX': [], 'GP': []}, 'BESTIP': {'HQ': '', 'EX': '', 'GP': ''}, 'TDXDIR': ''}
        config_file.write_text(json.dumps(write_data))

        with mock.patch('mootdx.config.CONF', str(config_file)):
            with mock.patch('mootdx.config.bestip') as mock_bestip:
                config.setup()
                mock_bestip.assert_not_called()  # config exists, bestip not triggered

    def test_setup_returns_bool(self, tmp_path):
        config_file = tmp_path / 'config.json'
        data = {'SERVER': {'HQ': [], 'EX': [], 'GP': []}, 'BESTIP': {'HQ': '', 'EX': '', 'GP': ''}, 'TDXDIR': ''}
        config_file.write_text(json.dumps(data))

        with mock.patch('mootdx.config.CONF', str(config_file)):
            result = config.setup()
            assert isinstance(result, bool)


class TestConfigPath:
    def test_path_returns_absolute_with_base(self):
        result = config.path('TDXDIR', 'subdir')
        assert isinstance(result, Path)


class TestConfigAll:
    """测试 config 模块 __all__ 中的所有函数"""
    def test_set_updates_settings(self):
        original = config.clone()
        try:
            config.set('TEST_VAL', 42)
            assert config.settings['TEST_VAL'] == 42
        finally:
            config.update(original)

    def test_update_merges_dicts(self):
        original = config.clone()
        try:
            config.update({'TEST_UPDATE': 'hello'})
            assert config.get('TEST_UPDATE') == 'hello'
        finally:
            config.update(original)
