# Testing Patterns

## Core Sections (Required)

### 1) Test Stack and Commands

- **无测试框架**: CMake 中无 `enable_testing()`、无 `add_test()`、无 GTest/Catch2 依赖（`CMakeLists.txt` 全文核实）
- 事实上的验证命令：

```bash
scripts/verify_sieve.sh        # 算法黄金值：重建 glm5_seastar_prime，跑 2×10⁹ 区间，
                               # 断言素数总数 == 98,222,287，不符 exit 1
scripts/check_environment.sh   # 环境：目录/命令/依赖逐项 [OK]/[FAIL]
./build.sh -r && ./build/release/prime_bench -t 32 -n 100000 -c 32
                               # 集成对账：10 用例素数总数互相对账（一致性校验）
```

- CI（`.github/workflows/build.yml`）: Debug/Release 矩阵构建 + `big_file_splitter` 冒烟（dd 生成 40MB 输入 → 分割 → ls 验证产物存在）

### 2) Test Layout

- `tests/` 仅含 `.gitkeep`——**目录为空**（`find tests -type f` 核实）
- 验证逻辑不在 tests/ 而在 `scripts/`（shell 黄金值校验）与 `src/prime_bench.cpp` 内（对账逻辑，`:174-190`）

### 3) Test Scope Matrix

| 层 | 机制 | 覆盖对象 | 缺口 |
|---|---|---|---|
| 算法正确性 | `verify_sieve.sh` 黄金值 | `prime_sieve.hpp`（π(2×10⁹)） | 边界区间、小区间、start≠0 未系统化 |
| 集成一致性 | `prime_bench` 对账 | 10 程序结果互相等价 | 仅在手动/CI 不跑 bench 时缺失 |
| 冒烟 | CI big_file_splitter | 文件分割器基本功能 | 无正确性断言（仅 ls） |
| 单元测试 | **无** | — | 调度分发、CLI 解析、CSV 写、双缓冲 I/O 全部无单测 |

### 4) Mocking and Isolation Strategy

无 mock——全部为真实运行（真实编译、真实多核、真实 DMA I/O）。与规范「真实测试优先于 mock」方向一致，但规范要求的单元/集成测试框架缺失。

### 5) Coverage and Quality Signals

- Coverage tool + threshold: 无工具；规范文本要求 >80%（`CLAUDE.md`「测试」）
- Current reported coverage: 未测量（无工具接入）→ `[ASK USER: 是否引入 GTest + CTest + gcov 落实规范]`

### 6) Evidence

- `CMakeLists.txt`（无测试基础设施）
- `scripts/verify_sieve.sh:14-25`（黄金值断言）
- `src/prime_bench.cpp:174-190`（对账逻辑）
- `.github/workflows/build.yml:24-28`（CI 冒烟步骤）
- `tests/.gitkeep`（空目录标记）
- `CLAUDE.md`「测试」与 `docs/project-rules.md`「测试规范」（规范 vs 现实差异源）
