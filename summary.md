# 工作摘要

**时间:** 2026-05-16

## 变更概要

### 适配 opentdx 0.5.x 接口变更
- **hq_adapter.py**: 适配层新增 `_clean_code`，统一裁剪股票代码中 `sh/sz/bj` 前缀/后缀，支持无点/带点/大小写混合等 6 种格式
- **pyproject.toml**: opentdx >= 0.5.0，pytest ^9.0，pytest-cov ^7.0

### 修正测试遗留引用
- **test_holiday.py**: holiday2→holiday_、holidays→_holiday，缓存文件名修正

## 版本
2.0.2 → 2.0.3
