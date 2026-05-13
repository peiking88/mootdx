import logging

import pandas as pd

logger = logging.getLogger(__name__)


def etf_reversion(data, xdxr, adjust='01'):
    if len(xdxr) <= 0:
        return data

    xdxr = xdxr.query('category==11')

    if len(xdxr) <= 0:
        return data

    data['date'] = pd.to_datetime(data[['year', 'month', 'day']], utc=False)

    data = data.set_index(['date'])
    data = pd.concat([data, xdxr.loc[data.index[0]: data.index[-1], ['suogu', 'category']]], axis=1)

    if adjust.lower() in ['01', 'qfq']:
        # 前复权向前移动一天
        # 向前传播
        data['suogu'] = data['suogu'].fillna(method='bfill')
        data['suogu'] = data['suogu'].fillna(1)
        data['suogu'] = data['suogu'].shift(-1)

        for col in ['open', 'high', 'low', 'close']:
            data[col] = data[col] / data['suogu']

    if adjust.lower() in ['02', 'hfq']:
        data['suogu'] = data['suogu'].fillna(method='ffill')
        data['suogu'] = data['suogu'].fillna(1)

        for col in ['open', 'high', 'low', 'close']:
            data[col] = data[col] * data['suogu']

    data = data.drop(['suogu', 'category'], axis=1, errors='ignore')
    data = data.set_index(['datetime'])

    return data


def reversion(symbol, stock_data, xdxr, type_='01'):
    def _fetch_xdxr(collections=None):
        """获取股票除权信息数据"""
        columns = [
            'category',
            'category_meaning',
            'date',
            'fenhong',
            'fenshu',
            'liquidity_after',
            'liquidity_before',
            'name',
            'peigu',
            'peigujia',
            'shares_after',
            'shares_before',
            'songzhuangu',
            'suogu',
            'xingquanjia',
        ]

        try:
            data = collections

            if len(data) <= 0:
                return data

            if 'date' not in data.columns:
                data['date'] = pd.to_datetime(data[['year', 'month', 'day']], utc=False)
                data = data.set_index(['date'])

            # data = data.drop(['year', 'month', 'day', ], axis=1)
            # data = pd.DataFrame([item for item in collections.find({"code": symbol})]).drop(["_id"], axis=1)
            # data = collections
            # data["date"] = pd.to_datetime(data["date"], utc=False)
            # data["date"] = pd.to_datetime(xdxr[["year", "month", "day"]], utc=False)
            # return data.set_index(["date", "code"], drop=False)
            return data
        except Exception as ex:
            logger.error(ex)
            return pd.DataFrame(data=[], columns=columns)

    # '股票 日线/分钟线 动态复权接口'
    # if isinstance(stock_data.index, pd.MultiIndex):
    #     symbol = stock_data.index.remove_unused_levels().levels[1][0]
    # else:
    #     symbol = stock_data["code"][0]
    # symbol = ''
    # symbol = (
    #     stock_data.index.remove_unused_levels().levels[1][0]
    #     if isinstance(stock_data.index, pd.MultiIndex)
    #     else stock_data["code"][0]
    # )

    if symbol[:2] in ['15', '16', '50', '51']:
        stock_data = etf_reversion(data=stock_data, xdxr=_fetch_xdxr(xdxr), adjust=type_)

    return stock_data
