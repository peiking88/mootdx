# 工作摘要

**时间:** 2026-05-09

## 变更概要

代码库全面清理：消除重复代码、删除死代码、修复异常使用、简化冗余逻辑。

### 重复代码消除
- 删除 `cache/timer.py` 和 `utils/timer.py` 两处重复 timeit 函数
- 删除 `utils/adjust.py` 中死代码 fq_factor（功能由 utils/factor.py 替代）
- ExHqAdapter 继承 StdHqAdapter，消除 close/__enter__/__exit__/_convert_period 重复
- 统一 consts.py 与 config.py 中重复的 CONFIG/settings 字典
- 删除 consts.py 中未使用的 FREQUENCY 列表
- 提取 quotes.py 重复验证逻辑：_check_market/_clamp_offset/_market_from_symbol
- 合并 hfq_bars/qfq_bars 为 _fq_bars，消除 19 行重复
- 提取 @retry 装饰器为 _retry 常量，10 处 50 行 → 10 行
- __main__.py action→frequency 字典化 + verbose 日志函数化

### 代码简化
- 整理 quotes.py imports（合并重复 import pandas，移动 class 定义位置）
- 删除 3 处 try/except Exception: raise 无操作反模式
- 删除 pool() 空桩函数
- _market_from_symbol: tuple-index 技巧 → 清晰 if/else 条件表达式

### 异常使用修复
- 4 处 raise Exception() 替换为 ValueError/FileNotFoundError 等具体类型
- MootdxModuleNotFoundError(Exception) → MootdxModuleNotFoundError(ImportError)
- 统一 ValidationException → MootdxValidationException
- 缩小 valid_server() 异常捕获范围

### 死代码删除
- 删除 utils/pandas_cache.py（无外部引用）
- 删除 cache/timed.py（生产代码无引用）
- 删除 scripts/examples/lru_cache.py（依赖已删除模块）
- 删除 tests/utils/test_timer.py（全注释，对应模块已删除）

## 最近提交
```
90a537b docs: 更新项目文档，新增依赖安装说明与变更日志，版本升至 0.15.1
ecb0ef5 feat: 新增 get_factor() 方法，删除死代码 demjson.py
0f5d5f5 解除 opentdx 循环依赖，内联常量定义并增强服务器发现兼容性
adcac09 同步项目配置、文档及杂项文件
04d3489 按规范整理项目目录结构
```
