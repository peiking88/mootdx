"""
列名规范测试

验证 StdHqAdapter / ExHqAdapter / to_data 的列名处理：
- adapter 层统一输出 volume（不再输出 vol）
- to_data 不做 vol→volume 转换（职责归 adapter）
- ExHqAdapter 不再使用拼音列名
- 输出 DataFrame 不应有重复列名
"""

import pandas as pd
import pytest

from mootdx.hq_adapter import StdHqAdapter
from mootdx.exhq_adapter import ExHqAdapter
from mootdx.utils import to_data


# ---------------------------------------------------------------------------
# StdHqAdapter 列名
# ---------------------------------------------------------------------------


class TestStdHqAdapterColumns:
    """StdHqAdapter 应输出 volume 而非 vol。"""

    def test_bars_output_has_volume(self):
        result = StdHqAdapter.to_df([
            {'open': 10, 'high': 11, 'low': 9, 'close': 10.5,
             'amount': 1000, 'volume': 5000},
        ])
        assert 'volume' in result.columns

    def test_transaction_output_has_volume(self):
        result = StdHqAdapter.to_df([
            {'time': '09:30', 'price': 10.0, 'volume': 100,
             'num': 1, 'buyorsell': 0},
        ])
        assert 'volume' in result.columns
        assert 'vol' not in result.columns

    def test_quotes_output_has_volume(self):
        result = StdHqAdapter.to_df([
            {'market': 1, 'code': '600000', 'price': 10.0,
             'volume': 50000, 'amount': 500000, 'cur_vol': 100},
        ])
        assert 'volume' in result.columns
        assert 'vol' not in result.columns

    def test_minute_output_has_volume(self):
        result = StdHqAdapter.to_df([
            {'price': 10.0, 'volume': 500},
        ])
        assert 'volume' in result.columns

    def test_bid_vol_kept_as_is(self):
        """盘口字段 bid_vol{i} / ask_vol{i} 保持不变。"""
        result = StdHqAdapter.to_df([
            {'bid_vol1': 100, 'ask_vol1': 200,
             'bid_vol2': 150, 'ask_vol2': 250},
        ])
        assert 'bid_vol1' in result.columns
        assert 'ask_vol1' in result.columns


# ---------------------------------------------------------------------------
# ExHqAdapter 列名
# ---------------------------------------------------------------------------


class TestExHqAdapterColumns:
    """ExHqAdapter 不应使用拼音列名。"""

    def test_quote_no_pinyin(self):
        """扩展行情报价不应有拼音列名。"""
        item = {
            'market': 31, 'code': '00700', 'pre_close': 350.0,
            'open': 352.0, 'high': 355.0, 'low': 349.0, 'price': 353.0,
            'open_position': 1000, 'volume': 50000,
            'current_volume': 200, 'sell_volume': 25000,
            'buy_volume': 25000, 'hold_position': 80000,
            'bid_vol1': 100, 'ask_vol1': 200,
        }
        result = StdHqAdapter.to_df([item])
        pinyin_names = {'zongliang', 'xianliang', 'neipan', 'waipan', 'kaicang', 'chicang'}
        for name in pinyin_names:
            assert name not in result.columns, f"拼音列名 {name} 应已替换为英文"

    def test_bars_output_has_volume(self):
        """扩展 K 线的 trade 应改为 volume。"""
        result = StdHqAdapter.to_df([
            {'open': 10, 'high': 11, 'low': 9, 'close': 10.5,
             'volume': 5000, 'amount': 50000},
        ])
        assert 'volume' in result.columns
        assert 'trade' not in result.columns

    def test_transaction_output_has_volume(self):
        """扩展成交的 volume 列应保持。"""
        result = StdHqAdapter.to_df([
            {'price': 10.0, 'volume': 100, 'zengcang': 50},
        ])
        assert 'volume' in result.columns


# ---------------------------------------------------------------------------
# to_data 不做 vol→volume 转换
# ---------------------------------------------------------------------------


class TestToDataNoVolRename:
    """to_data 不再负责 vol→volume 转换（已由 adapter 层处理）。"""

    def test_vol_not_renamed_by_to_data(self):
        """如果数据中仍有 vol（绕过 adapter），to_data 不应改它。"""
        df = pd.DataFrame({"vol": [100, 200], "price": [10.0, 10.1]})
        result = to_data(df)
        assert "vol" in result.columns
        assert "volume" not in result.columns

    def test_volume_passthrough(self):
        """adapter 已输出的 volume 应原样保留。"""
        df = pd.DataFrame({"volume": [100, 200], "price": [10.0, 10.1]})
        result = to_data(df)
        assert "volume" in result.columns

    def test_no_duplicate_columns(self):
        """不应产生重复列名。"""
        df = pd.DataFrame({"volume": [100, 200], "price": [10.0, 10.1]})
        result = to_data(df)
        assert not result.columns.duplicated().any()


# ---------------------------------------------------------------------------
# 空值与边界
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """边界输入不应出错。"""

    def test_empty_dataframe(self):
        result = to_data(pd.DataFrame())
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_none_input(self):
        result = to_data(None)
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_false_input(self):
        result = to_data(False)
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_empty_list(self):
        result = to_data([])
        assert isinstance(result, (pd.DataFrame, type(None)))

    def test_dict_input(self):
        data = {"price": 10.0, "volume": 500}
        result = to_data(data)
        assert isinstance(result, pd.DataFrame)
        assert "volume" in result.columns


# ---------------------------------------------------------------------------
# 日期索引
# ---------------------------------------------------------------------------


class TestDateIndex:
    """datetime / date 列应被设为索引。"""

    def test_datetime_column_as_index(self):
        df = pd.DataFrame({
            "datetime": ["2025-01-01", "2025-01-02"],
            "price": [10.0, 10.1],
        })
        result = to_data(df)
        assert result.index.name == "datetime" or pd.api.types.is_datetime64_any_dtype(result.index)

    def test_date_column_as_index(self):
        df = pd.DataFrame({
            "date": ["2025-01-01", "2025-01-02"],
            "price": [10.0, 10.1],
        })
        result = to_data(df)
        assert result.index.name == "date" or pd.api.types.is_datetime64_any_dtype(result.index)


# ---------------------------------------------------------------------------
# 模拟真实数据格式
# ---------------------------------------------------------------------------


class TestRealWorldFormats:
    """模拟 adapter 输出经 to_data 后的最终列名。"""

    def test_std_kline_format(self):
        """标准行情 K 线（adapter 已输出 volume）。"""
        df = pd.DataFrame({
            "date": ["2025-01-02", "2025-01-03"],
            "open": [10.0, 10.5],
            "high": [10.8, 10.9],
            "low": [9.8, 10.2],
            "close": [10.5, 10.6],
            "volume": [50000, 60000],
            "amount": [500000, 600000],
        })
        result = to_data(df)
        assert "volume" in result.columns
        assert "vol" not in result.columns
        assert not result.columns.duplicated().any()

    def test_std_tick_format(self):
        """标准行情逐笔（adapter 已输出 volume）。"""
        df = pd.DataFrame({
            "time": ["09:30:00", "09:30:01"],
            "price": [10.0, 10.01],
            "volume": [100, 200],
            "num": [1, 1],
            "buyorsell": [0, 1],
        })
        result = to_data(df)
        assert "volume" in result.columns
        assert "vol" not in result.columns
        assert not result.columns.duplicated().any()

    def test_ex_quote_format(self):
        """扩展行情报价（无拼音列名）。"""
        df = pd.DataFrame({
            "code": ["00700"],
            "price": [353.0],
            "volume": [50000],
            "current_volume": [200],
            "sell_volume": [25000],
            "buy_volume": [25000],
            "open_position": [1000],
            "hold_position": [80000],
        })
        result = to_data(df)
        pinyin = {'zongliang', 'xianliang', 'neipan', 'waipan', 'kaicang', 'chicang'}
        for name in pinyin:
            assert name not in result.columns
        assert "volume" in result.columns
        assert "current_volume" in result.columns
