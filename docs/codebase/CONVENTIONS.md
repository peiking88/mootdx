# Coding Conventions

## Core Sections (Required)

### 1) Naming Rules

- **文件**: snake_case，模式 `<别名>_<框架>_<功能>.cpp`（`glm5_seastar_prime.cpp`）；共享头 `prime_sieve.hpp`
- **命名空间**: `prime::`（算法共享层，`src/prime_sieve.hpp:14`）
- **函数/变量**: snake_case（`segmented_sieve`、`run_program`）；局部常量 `k` 前缀 PascalCase（`kBufSize`，`src/gemma4_seastar_prime.cpp:60`）
- **结构体**: 简单 POD 大写开头（`Task`、`TaskResult`，`src/gemma4_seastar_prime.cpp:22-32`）
- **模型别名约定**: 各 LLM 代号前缀是各实现的署名，新增变体沿用此惯例 `[ASK USER: 新程序是否继续用模型别名命名]`

### 2) Formatting and Linting

- `.clang-format`: **Mozilla 基线**，ColumnLimit 80，`BreakBeforeBraces: Attach`，`ContinuationIndentWidth: 2`，`IncludeBlocks: Regroup`
- 编译警告: CMake 全局追加 `-w -Wno-error`（`CMakeLists.txt:225`）——**关闭所有警告**，见 CONCERNS.md R-4
- Release: `-O3 -DNDEBUG`；Debug: `-g -O2 -fno-omit-frame-pointer -rdynamic`（`CMakeLists.txt:219-223`）
- 无独立 linter（无 clang-tidy/cppcheck 配置）

### 3) Import and Module Conventions

- include 顺序: 框架头（seastar/*）→ boost → 标准库 → 本地头（`src/gemma4_seastar_prime.cpp:1-20` 实例），与 `.clang-format` Regroup 规则一致
- 唯一本地共享头: `#include "prime_sieve.hpp"`；禁止 include 其他程序的 `.cpp`

### 4) Error and Logging Conventions

- **C++ 侧**: 非致命异常路径 `std::cerr << "警告: ..."` + 继续（`src/prime_bench.cpp:267` mkdir EEXIST 模式）；Seastar 程序日志走框架 `seastar::logger`，`-l` 控制，默认 `error`（`README.md:109`）
- **脚本侧**: `set -euo pipefail` + 显式 `[OK]/[WARN]/[FAIL]` 前缀输出（`scripts/check_environment.sh:5`、`scripts/verify_sieve.sh:4`）
- **黄金值校验**: `verify_sieve.sh` 硬编码期望 `98222287`，不符即 `exit 1`（`scripts/verify_sieve.sh:22-25`）
- **中文输出**: 面向用户的日志/表格全部中文（`素数总数:`、`[1/10] 运行 …`），遵守 `CLAUDE.md`「语言」规约

### 5) Testing Conventions

- 规范要求（`CLAUDE.md`「测试」）: 覆盖率 >80%、单元+集成测试、真实优先于 mock、先激活虚拟环境
- 现实: `tests/` 为空，无测试框架注册于 CMake（无 enable_testing/CTest/add_test）→ 见 TESTING.md 与 CONCERNS.md R-1
- 事实上的验证: 算法黄金值（verify_sieve.sh）+ CI 冒烟（big_file_splitter）+ bench 内置对账

### 6) Evidence

- `.clang-format`（全量格式规则）
- `CMakeLists.txt:219-225`（编译旗标与 -w）
- `src/gemma4_seastar_prime.cpp:1-20,22-60`（命名/include/常量实例）
- `src/prime_bench.cpp:265-268`（错误处理实例）
- `scripts/check_environment.sh:1-40`、`scripts/verify_sieve.sh`（脚本规约）
- `docs/project-rules.md`「语言规范」「测试规范」
