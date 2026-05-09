import unittest

from mootdx.quotes import Quotes
from tests.conftest import skip_if_no_network


class TestAdjust2(unittest.TestCase):
    client = None

    # 初始化工作
    def setup_class(self):
        skip_if_no_network()
        self.client = Quotes.factory(market='std', timeout=10)  # 标准市场

    # 退出清理工作
    def teardown_class(self):
        self.client.client.close()
        del self.client

    def test_to_qfq(self):
        result = self.client.bars(symbol='600036', adjust='qfq', offset=10)
        self.assertFalse(result.empty)

    def test_to_hfq(self):
        result = self.client.bars(symbol='600036', adjust='hfq', offset=10)
        self.assertFalse(result.empty)
