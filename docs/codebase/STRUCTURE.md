# Codebase Structure

## Core Sections (Required)

### 1) Top-Level Map

| 目录/文件 | 用途 | 现状 |
|---|---|---|
| `src/` | 业务源码：12 个 `.cpp`（3345 行）+ 共享头 `prime_sieve.hpp` | 全部产品代码在此 |
| `external/` | 第三方依赖子模块（seastar、libfork） | 禁改禁提交 |
| `build/` | 构建输出（`release/`、`debug/`） | 不提交 |
| `output/` | 运行输出 CSV（默认路径，commit `a856c4b` 统一） | 不提交；当前磁盘堆积约 982MB |
| `scripts/` | `check_environment.sh`、`verify_sieve.sh` | 2 个维护脚本 |
| `tests/` | 测试目录 | **空**（仅 `.gitkeep`） |
| `cfg/` | 配置目录 | **空**（仅 `.gitkeep`） |
| `docs/` | `api.md`、`project-rules.md`、`iotune-manual.md`、`codebase/`（本文档集） | — |
| `.claude/`、`.pilotdeck/` | 代理协作配置与技能库 | 与产品代码无关 |
| 根文件 | `CMakeLists.txt`、`build.sh`、`VERSION`、`.clang-format`、`README.md`、`summary.md`、`CLAUDE.md` | — |

### 2) Entry Points

每个 `.cpp` 均为独立 `main`（`CMakeLists.txt:235-271`）：

| 可执行 | 行数 | 角色 |
|---|---|---|
| `prime_bench` | 334 | 基准编排器：fork+execvp 依次运行 10 个素数程序并对账（`src/prime_bench.cpp:272-324`） |
| `sequence_prime` | 238 | 顺序基线 |
| `glm5_seastar_prime` | 257 | Seastar 集中队列 + atomic |
| `minimax_seastar_prime` | 296 | Seastar 工作窃取 |
| `sonnet46_seastar_prime` | 308 | Seastar 分段筛法（32 核设计） |
| `kimi_seastar_prime` | 248 | Seastar 集中队列 + atomic fetch_add |
| `dk4_seastar_prime` | 227 | Seastar 集中队列 + seastar::async |
| `gemma4_seastar_prime` | 227 | Seastar 蛇形 Round-Robin + dma 双缓冲 |
| `longcat_seastar_prime` | 277 | Seastar 集中队列 + std::mutex |
| `glm5_libfork_prime` | 355 | libfork 共享队列 + 工作窃取 |
| `minimax_libfork_prime` | 336 | libfork 主线程队列 + 工作线程 |
| `big_file_splitter` | 242 | Seastar 大文件分割器 |

### 3) Module Boundaries

- **共享算法层**: `src/prime_sieve.hpp` —— 位压缩奇数分段筛法（1 bit/奇数，16 倍内存节省），所有素数程序 include 它，"避免代码重复"（`src/prime_sieve.hpp:2-4`）。修改它必须跑 `scripts/verify_sieve.sh`（该脚本头注释）。
- **程序间零耦合**: 素数程序互不调用、互不 include；唯一交互点是 `prime_bench` 以子进程方式运行它们并解析 stdout 的 `素数总数:` 行（`README.md:164`）。
- **external/ 硬边界**: 依赖问题只能在上游解决，本仓不改。

### 4) Naming and Organization Rules

- 文件命名: `<模型别名>_<框架>_<功能>.cpp`（如 `gemma4_seastar_prime.cpp`）；模型别名来自各 LLM 代号（glm5/minimax/kimi/dk4/gemma4/longcat/sonnet46），是各实现的"作者署名"而非功能描述
- 共享代码: `src/prime_sieve.hpp`，`prime::` 命名空间
- 新程序落位惯例: `src/<name>.cpp` + `CMakeLists.txt` 注册 `add_executable` + `README.md` 表格 + `docs/api.md` + `prime_bench` 用例注册（见 WORKFLOWS.md WF2）

### 5) Evidence

- `CMakeLists.txt:235-271`（12 个 add_executable 及链接库）
- `src/prime_sieve.hpp:1-15`（共享边界声明）
- `wc -l src/*.cpp`（行数）
- 目录现状: `find tests cfg -type f` → 仅 `.gitkeep`
- `docs/project-rules.md`「目录规范」与 `CLAUDE.md`「目录约定」
