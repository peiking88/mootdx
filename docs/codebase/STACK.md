# Technology Stack

## Core Sections (Required)

### 1) Runtime Summary

- **语言**: C++20（`CMakeLists.txt:213` `CMAKE_CXX_STANDARD 20`，`EXTENSIONS OFF`）
- **构建系统**: CMake ≥ 3.14 + Ninja（`CMakeLists.txt:2`、`build.sh:118-124`）
- **运行形态**: 本地命令行可执行程序集合（无服务、无守护进程），12 个独立 `add_executable` 目标（`CMakeLists.txt:235-271`）
- **目标平台**: Ubuntu 25.10+（GCC 15.2.0 / Clang 16，`README.md:44`）；CI 跑 ubuntu-22.04（`.github/workflows/build.yml:6`）

### 2) Production Frameworks and Dependencies

| 依赖 | 角色 | 引入方式 |
|---|---|---|
| Seastar（scylladb/seastar） | share-nothing 异步框架，8 个素数程序 + 文件分割器 | git 子模块 `external/seastar`（`.gitmodules:1-3`），`add_subdirectory` 静态链入 |
| libfork（ConorWilliams/libfork） | fork-join 并行框架，2 个素数程序 | git 子模块 `external/libfork`（`.gitmodules:5-7`） |
| Boost.program_options | Seastar 程序 CLI 解析（随 Seastar 传递依赖） | 系统安装，`src/gemma4_seastar_prime.cpp:11` |
| POSIX 线程 / 标准库 | libfork 程序与 `sequence_prime`/`prime_bench` 无额外依赖 | 标准库 |

第三方依赖规则：`external/` 禁止修改、禁止提交（`CLAUDE.md`「必须遵循」）；Seastar 系统依赖通过 `./external/seastar/install-dependencies.sh` 安装（`README.md:59`）。

### 3) Development Toolchain

- 编译器: GCC 15+ 或 Clang 14+（`README.md:42`）
- 构建驱动: `build.sh`（`-r` Release / `-d` Debug / `-a` 两者 / `-c` 清理 / `-j N` 并行，默认 `$(nproc)`）
- 格式化: `.clang-format`（Mozilla 风格基线，80 列，`Attach` 大括号）
- CI: GitHub Actions，PR 触发，Debug/Release 矩阵构建 + `big_file_splitter` 冒烟（`.github/workflows/build.yml`）
- 环境检查: `scripts/check_environment.sh`（目录/命令/依赖完整性，初始化后必须运行）
- 版本管理: 根目录 `VERSION` 文件（当前 `2.0.6`），CMake 读取为项目版本（`CMakeLists.txt:4-5`）

### 4) Key Commands

```bash
# 环境初始化
git submodule update --init --recursive
./external/seastar/install-dependencies.sh
scripts/check_environment.sh

# 构建（Release，全量目标）
./build.sh -r -j $(nproc)
# 构建单个目标
./build.sh -r -j $(nproc) prime_bench

# 运行基准（10 用例）
./build/release/prime_bench -t 32 -n 100000 -c 32

# 算法正确性黄金值校验（π(2×10⁹) = 98,222,287）
scripts/verify_sieve.sh

# 单程序运行（统一 CLI）
./build/release/minimax_seastar_prime -t 20 -n 100000 -c 4 -o output/x.csv
```

### 5) Environment and Config

- Required env vars: `GIT_USERNAME`, `GIT_PASSWORD`（仅 Git 推送认证用，非程序运行时依赖；`CLAUDE.md`「Git 认证」）
- 程序运行时无必需环境变量；全部配置走 CLI 参数（`-t/-n/-o/-l/-c`，`docs/api.md`「通用约定」）
- `cfg/` 目录存在但为空（仅 `.gitkeep`）——项目规范模板预留，实际未使用 `[ASK USER]`

### 6) Evidence

- `CMakeLists.txt`（语言标准、依赖接线、12 个目标）
- `.gitmodules`、`VERSION`、`.clang-format`
- `build.sh:30-124`（参数与 cmake/ninja 调用）
- `.github/workflows/build.yml`
- `README.md:40-91`（系统要求与命令）
- `docs/api.md`（CLI 契约）
