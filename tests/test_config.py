import copy
import json
from pathlib import Path
from unittest import mock

import pytest

from mootdx import config
from mootdx.consts import EX_HOSTS, GP_HOSTS, HQ_HOSTS


class TestConfigSetGet:
    def test_set_and_get(self):
        config.set('test_key', 'test_value')
        assert config.get('test_key') == 'test_value'

    def test_get_missing_top_key(self):
        result = config.get('NONEXISTENT_KEY_XYZ')
        assert result is None

    def test_get_nested_key(self):
        config.set('SERVER', {'HQ': [('s1', '1.2.3.4', 7709)]})
        result = config.get('SERVER.HQ')
        assert result == [('s1', '1.2.3.4', 7709)]

    def test_get_nested_default(self):
        config.set('SERVER', {'HQ': []})
        result = config.get('SERVER.NONEXISTENT', 'fallback')
        assert result == 'fallback'

    def test_get_deep_nested(self):
        config.set('DEEP', {'a': {'b': {'c': 42}}})
        # get('DEEP.a.b.c') walks: settings['DEEP'] → get('a') → get('b') → get('c')
        result = config.get('DEEP.a.b.c')
        assert result == 42

    def test_has(self):
        config.set('LIST', [1, 2, 3])
        assert config.has('LIST', 2) is True
        assert config.has('LIST', 999) is False


class TestClone:
    def test_clone_returns_deep_copy(self):
        config.set('MUTABLE', {'a': 1})
        cloned = config.clone()
        cloned['MUTABLE']['a'] = 999
        assert config.get('MUTABLE')['a'] == 1


class TestUpdate:
    def test_update_merges(self):
        original = config.clone()
        config.update({'NEW_KEY': 'new_value'})
        assert config.get('NEW_KEY') == 'new_value'
        # restore
        config.update(original)


class TestPath:
    def test_path_returns_path(self):
        result = config.path('TDXDIR', 'subdir')
        assert isinstance(result, Path)


class TestModuleAttributes:
    def test_all_exports(self):
        expected = ['set', 'get', 'copy', 'update', 'settings']
        for name in expected:
            assert name in config.__all__

    def test_settings_structure(self):
        assert 'SERVER' in config.settings
        assert 'BESTIP' in config.settings
        assert 'TDXDIR' in config.settings
