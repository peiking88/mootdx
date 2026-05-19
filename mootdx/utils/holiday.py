import datetime
import re
from io import StringIO
from pathlib import Path

import httpx
import pandas as pd

from mootdx import get_config_path
from mootdx.cache import file_cache
from mootdx.logger import logger


def holiday(date=None, format_=None, country=None, result=False):
    format_ = format_ if format_ else '%Y-%m-%d'
    country = country if country else '中国'

    try:
        if date:
            date = datetime.datetime.strptime(date, format_).date()
        else:
            date = datetime.datetime.now().date()
    except ValueError as ex:
        logger.error('日期或者日期格式错误!')
        return None

    df = _holiday()

    if country not in list(set(df['国家'].values)):
        logger.error(f'没有该国家`{country}`的交易日数据')
        return None

    df = df[df['国家'] == country]
    df = df[df['日期'] == pd.Timestamp(date)]

    if result:
        return df

    logger.debug(date.weekday())

    return not df.empty or date.weekday() >= 5


@file_cache(filepath=get_config_path('caches/holiday.plk'), refresh_time=3600 * 24)
def _holiday():
    logger.debug('调用远程接口')
    res = httpx.get('https://www.tdx.com.cn/url/holiday/')

    res.encoding = 'gbk'
    ret = re.findall(r'<textarea id="data" style="display:none;">([\s\w\W]+)</textarea>', res.text, re.M)[0].strip()

    df = pd.read_csv(StringIO(ret), sep='|')
    df = df.iloc[:, :4]

    df.columns = ['日期', '节日', '国家', '交易所']
    df['日期'] = pd.to_datetime(df['日期'].astype('str'), format='%Y%m%d')

    if df.empty:
        Path(get_config_path('caches/holiday.plk')).unlink(missing_ok=True)
        return pd.DataFrame([])

    return df


def holiday_(date=None, format_=None, country=None):
    return holiday(date=date, format_=format_, country=country, result=True)
