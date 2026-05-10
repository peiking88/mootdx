import socket

import pandas
import pytest

from mootdx.quotes import Quotes


def is_empty(obj):
    if isinstance(obj, pandas.DataFrame):
        return obj.empty

    return not obj


def is_network_available(timeout=2):
    """检测 TDX 服务器是否可达，依次尝试 opentdx 服务器列表"""
    try:
        from opentdx.const import main_hosts
        hosts = [(h[1], h[2]) for h in main_hosts[:6]]  # 取前6个测速
    except Exception:
        hosts = [('110.41.147.114', 7709)]

    for host, port in hosts:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            continue
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
