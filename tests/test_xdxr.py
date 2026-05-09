import unittest
from pathlib import Path

from mootdx import get_config_path
from mootdx.utils.adjust import get_xdxr
from tests.conftest import skip_if_no_network


class XDXRTestCase(unittest.TestCase):
    symbol = '600000'

    def setUp(self):
        skip_if_no_network()

    def test_no_cache(self):
        Path(get_config_path(f'xdxr/{self.symbol}.plk')).unlink(missing_ok=True)
        xdxr = get_xdxr(symbol=self.symbol)

        assert xdxr.empty is False
        assert 'code' in xdxr.columns, xdxr.columns

    def test_cached(self):
        xdxr = get_xdxr(symbol=self.symbol)
        xdxr = get_xdxr(symbol=self.symbol)

        assert xdxr.empty is False
        assert 'code' in xdxr.columns, xdxr.columns
