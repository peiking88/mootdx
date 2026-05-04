import pytest


def test_quotes(quotes):
    quotes.close()
    assert quotes.xdxr(symbol='600036').empty is False
