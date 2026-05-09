# 工作摘要

**时间:** 2026-05-09

## 代码重构

1. 删除死代码：`stock_bj_a()`（76行）、`gpcw()`（23行）、`config.has()`
2. 修复 `config.__all__` 与实际函数名不匹配（`copy` → `clone`）
3. 内联 `check_server` 薄包装，消除不必要间接层
4. 命名 `get_k_data` 中的魔数（2.8 → `_OFFSET_FACTOR_NEAR`，3.5 → `_OFFSET_FACTOR_FAR`）

**影响文件**：8个，-178行 +17行。311个测试全部通过。

## 最近提交
```
b155413 chore: 版本升至 0.15.2
e32c383 清理: 消除重复代码、删除死代码、修复异常使用
90a537b docs: 更新项目文档，新增依赖安装说明与变更日志，版本升至 0.15.1
ecb0ef5 feat: 新增 get_factor() 方法，删除死代码 demjson.py
0f5d5f5 解除 opentdx 循环依赖，内联常量定义并增强服务器发现兼容性
```
