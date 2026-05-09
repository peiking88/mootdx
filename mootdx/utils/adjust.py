from pathlib import Path

import pandas as pd

from mootdx import get_config_path
from mootdx.cache import file_cache
from mootdx.quotes import Quotes


def get_xdxr(symbol):
    @file_cache(filepath=Path(get_config_path(f'xdxr/{symbol}.plk')), refresh_time=3600 * 24)
    def _xdxr(symbol):
        xdxr = Quotes.factory('std').xdxr(symbol=symbol)

        if xdxr.empty:
            return xdxr

        xdxr['code'] = symbol
        xdxr['date'] = pd.to_datetime(xdxr[['year', 'month', 'day']], utc=False)

        return xdxr.set_index(['date'])

    return _xdxr(symbol)


def to_adjust(temp_df, symbol=None, adjust=None):
    from mootdx.tools.reversion import reversion
    return reversion(symbol, temp_df, get_xdxr(symbol), adjust)


