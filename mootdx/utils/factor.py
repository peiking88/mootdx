import ast

import httpx
import pandas as pd

from mootdx.logger import logger
from mootdx.utils import get_stock_market


def fetch_factor_from_sina(symbol: str, method: str) -> pd.DataFrame:
    """从新浪财经获取完整复权因子序列。

    Args:
        symbol: 股票代码，如 '600036' 或 'sh600036'
        method: 复权类型 'qfq'（前复权）或 'hfq'（后复权）

    Returns:
        pd.DataFrame，以 date 为索引，包含 factor 列。获取失败返回空 DataFrame。
    """
    code = symbol.replace("sh", "").replace("sz", "").replace("bj", "")
    market = get_stock_market(code, string=True)
    full_symbol = f"{market}{code}"

    url = f"https://finance.sina.com.cn/realstock/company/{full_symbol}/{method}.js"
    try:
        rsp = httpx.get(url, timeout=10)
        rsp.raise_for_status()
    except Exception as e:
        logger.error(f"Sina factor request failed for {full_symbol} {method}: {e}")
        return pd.DataFrame(columns=["date", "factor"])

    # Sina returns JS like: var data_xxx = {...};
    if "=" not in rsp.text:
        logger.error(f"Unexpected Sina response format for {full_symbol}: no '=' found")
        return pd.DataFrame(columns=["date", "factor"])

    raw = rsp.text.split("=", 1)[1].split("\n", 1)[0].strip().rstrip(";")

    try:
        data = ast.literal_eval(raw)
    except (ValueError, SyntaxError) as e:
        logger.error(f"Failed to parse Sina factor data for {full_symbol} {method}: {e}")
        return pd.DataFrame(columns=["date", "factor"])

    if not isinstance(data, dict) or "data" not in data:
        logger.error(
            f"Unexpected Sina response structure for {full_symbol}: {type(data).__name__}"
        )
        return pd.DataFrame(columns=["date", "factor"])

    records = data["data"]
    dates = pd.to_datetime([r["d"] for r in records], errors="coerce")
    factors = [float(r["f"]) for r in records]
    factor_df = pd.DataFrame({"date": dates, "factor": factors})
    factor_df = factor_df.dropna(subset=["date"])
    factor_df = factor_df.loc[factor_df["date"] >= pd.Timestamp("1990-01-01")].copy()
    factor_df = factor_df.set_index("date").sort_index()
    return factor_df
