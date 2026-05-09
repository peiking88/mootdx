import logging
import unittest

from mootdx.logger import logger
from mootdx.quotes import Quotes
from tests.conftest import skip_if_no_network


class TestBestIP(unittest.TestCase):
    def setup(self):
        skip_if_no_network()
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        logger.addHandler(ch)
        logger.setLevel(logging.DEBUG)

    def test_normal(self):
        Quotes.factory(market='std', bestip=True)
