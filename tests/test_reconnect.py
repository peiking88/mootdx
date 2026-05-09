import pytest

from tests.conftest import skip_if_no_network


def test_quotes(quotes):
    skip_if_no_network()
    quotes.close()
    assert quotes.xdxr(symbol='600036').empty is False
