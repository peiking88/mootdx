import pytest

from mootdx.logger import logger
from mootdx.quotes import Quotes
from mootdx.reader import Reader
from tests.conftest import is_network_available


class TestFactor:

    # 初始化工作
    def setup_class(self):
        self.client = Quotes.factory(market='std', timeout=10)  # 标准市场
        self.reader = Reader.factory(market='std', tdxdir='tests/fixtures')
        logger.debug('初始化工作')

    @pytest.mark.skipif(not is_network_available(), reason='网络不可达')
    def test_qfq_factor(self):
        result = self.client.bars(symbol='600036', adjust='qfq', offset=10)
        assert len(result), result

    @pytest.mark.skipif(not is_network_available(), reason='网络不可达')
    def test_hfq_factor(self):
        result = self.client.bars(symbol='600036', adjust='hfq', offset=10)
        assert len(result), result

    def test_reader_qfq(self):
        result = self.reader.daily(symbol='688001', adjust='qfq')
        assert not result.empty, '股票代码不存在'
        logger.debug(result.tail())

    def test_reader_hfq(self):
        result = self.reader.daily(symbol='688001', adjust='hfq')
        assert not result.empty, '股票代码不存在'
        logger.debug(result.tail())
