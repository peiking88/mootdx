import socket

import pandas
import pytest

from mootdx.quotes import Quotes


def is_empty(obj):
    if isinstance(obj, pandas.DataFrame):
        return obj.empty

    return not obj


def is_network_available(host='39.100.68.59', port=7709, timeout=2):
    """检测 TDX 服务器是否可达"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def skip_if_no_network(reason='网络不可达，跳过真实测试'):
    """当网络不可达时跳过测试"""
    if not is_network_available():
        pytest.skip(reason)


@pytest.fixture()
def quotes():
    return Quotes.factory('std')

# @pytest.fixture()
# def reader():
#     return Reader.factory("std")
