import pytest

from mootdx.quotes import Quotes
from mootdx.utils import FREQUENCY
from tests.conftest import is_network_available


@pytest.fixture(scope='function')
def client():
    return Quotes.factory(market='std')


@pytest.mark.parametrize('i,v', [(i, v) for i, v in enumerate(FREQUENCY)])
@pytest.mark.skipif(not is_network_available(), reason='网络不可达')
def test_to_data_empty(client, i, v):
    assert all(client.bars(symbol='600036', frequency=i) == client.bars(symbol='600036', frequency=v))
