# 工作摘要

**时间:** 2026-05-10

## 变更概要

### 库日志规范化
- `logger.py` 库化：导入时不再配置 handler（仅添加 NullHandler），新增 `setup_logging()` 函数供 CLI 入口调用
- `__main__.py` entry() 中调用 `setup_logging()` 启用控制台日志

### 代码清理
- `quotes.py`：移除全局 `instance` 变量及 `check_empty()` 中的自动重连副作用逻辑
- `server.py`：移除 tdxpy 兼容导入，统一使用 opentdx
- `utils/factor.py`：用 `ast.literal_eval` 替代 `eval`，移除文件缓存，函数重命名为 `fetch_factor_from_sina`
- `tools/reversion.py`：适配函数重命名

### 功能增强
- `quotes.py` `get_factor()` 新增新浪财经回退路径（TDX 数据为空时自动回退）
- 新增 `_get_factor_from_tdx()` 内部方法，增强异常处理
- `tools/customize.py` `_blocknew()` 增加空 symbol 校验

### 测试加固
- `conftest.py` 新增 `skip_if_no_network()` / `is_network_available()`
- 所有真实测试增加网络检测跳过（避免 TDX 服务器不可达时假失败）
- 多处真实测试减少数据量（offset 从 800 降到 10），符合 CLAUDE.md 规范
- `test_quotes_unit.py` 新增 `TestCheckMarket`、`TestClampOffset`、`TestMarketFromSymbol`
- `test_customize.py` 精确化异常断言（`pytest.raises` 匹配具体异常类型和消息）
- 删除 `test_adapter_tdxpy.py`，新增 `test_adapter_opentdx.py`、`test_main.py`

### 版本
- `0.15.3` → `0.15.4`

## 跳过测试分析

全量测试 339 个，通过 276，跳过 63（18.6%）。跳过原因：
- **TDX 服务器不可达**：57 个（90.5%），`skip_if_no_network()` 在 setup 阶段检测到 `39.100.68.59:7709` 超时
- **硬编码跳过**：2 个（3.2%），`test_useless.py` 中破坏性 pip 操作标记为"暂时不做重复测试"
- **功能缺失**：2 个（3.2%），非交易时间逐笔成交 + 北交所支持不完整
- **未触发**：`test_holiday.py` 中 3 个 `py_mini_racer` 条件跳过，当前环境已安装
