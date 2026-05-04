# 工作摘要

**时间:** 2026-05-04

## 变更概要

新增 12 个单元测试文件，将测试覆盖率从 64% 提升至 80%（+173 测试用例）。

### 新增测试文件

- test_tdxfinder.py: tdxfinder 完整单元测试（0%→100%）
- test_exceptions.py: 全部异常类测试（59%→100%）
- test_config.py: config 模块 set/get/has/clone 等测试（65%→84%）
- test_config_setup.py: config.setup() 流程测试
- test_hq_adapter.py: to_df/_parse_date/上下文管理器测试（74%→87%）
- test_exhq_adapter.py: connect 参数/上下文管理器测试（80%→89%）
- test_quotes_unit.py: valid_server/check_empty/BaseQuotes 测试（71%→91%）
- test_quotes_more.py: StdQuotes F10/block/finance/xdxr 等测试
- test_quotes_opentdx.py: opentdx 依赖方法测试
- test_server_unit.py: connect 函数测试（53%→71%）
- test_server_more.py: server/bestip/check_server 测试
- test_adapter_tdxpy.py: 适配器 tdxpy 后端委托方法全测试

### 覆盖率变化

| 指标 | 之前 | 之后 |
|------|------|------|
| 总覆盖率 | 64% | 80% |
| 总测试数 | 143 | 316 |
| 测试文件数 | 31 | 42 |
