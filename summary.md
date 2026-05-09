# 工作摘要

**版本:** 0.13.0

## 核心变更：迁移至 opentdx 纯依赖

彻底移除 tdxpy 依赖，全部功能迁移至 opentdx 0.3.0。

### 源码依赖迁移
- mootdx/reader.py: tdxpy.reader → opentdx.reader
- mootdx/parse.py: tdxpy.reader.BlockReader → opentdx.utils.block_reader
- mootdx/tools/customize.py: tdxpy.reader.CustomerBlockReader → opentdx.utils.block_reader
- mootdx/contrib/compat.py: TdxDailyBarReader 从 opentdx 导入；删除未使用的 MooBaseSocketClient

### 配置清理
- pyproject.toml: 移除 tdxpy 依赖项
- requirements.txt: 移除 tdxpy
- tox.ini: 移除 tdxpy

### 测试重写
- test_adapter_tdxpy.py 重写为 opentdx 委托测试
- test_hq_adapter.py: 移除 tdxpy 回退测试；更新 MARKET/PERIOD 枚举断言
- test_exhq_adapter.py: 移除 _backend 属性检查

### API 文档
- docs/api/quote1.md: 新增板块列表、资金流向、竞价、异动等 11 个方法
- docs/api/quote2.md: 更新扩展市场说明
- docs/index.md: pytdx/tdxpy → opentdx

### 测试结果
314 passed, 4 skipped, 0 failures
