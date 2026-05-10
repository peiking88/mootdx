# 工作摘要

**时间:** 2026-05-10

## 变更概要

版本升级至 0.16.0 — 适配器列名规范化重构

### StdHqAdapter (hq_adapter.py)
- K线/分时/成交的 `vol` 输出统一改为 `volume`
- 实时行情：`last_close` → `pre_close`、`cur_vol` → `current_volume`、`s_vol` → `sell_volume`、`b_vol` → `buy_volume`
- 逐笔成交：`buyorsell` → `direction`

### ExHqAdapter (exhq_adapter.py)
- 扩展行情报价：`zongliang` → `volume`、`xianliang` → `current_volume`、`neipan` → `sell_volume`、`waipan` → `buy_volume`、`kaicang` → `open_position`、`chicang` → `hold_position`，补充 `amount` 字段
- 扩展 K 线：`trade` → `volume`，移除冗余 `price` 字段
- 扩展成交：`zengcang` → `position_change`

### to_data (utils/__init__.py)
- 移除 `vol→volume` 转换逻辑（职责归 adapter 层）

### 测试
- 新增 `tests/test_to_data_columns.py`：21 个列名规范测试用例
- 全部 360 个测试通过
