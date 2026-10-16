# External Integrations

## Core Sections (Required)

### 1) Integration Inventory

本项目是**纯本地计算基准**——无外部 API 调用、无数据库、无消息队列、无网络服务。全部"集成"为开发/交付侧：

| 集成点 | 类型 | 证据 |
|---|---|---|
| GitHub（peiking88/mootdx） | Git 远程 + Actions CI | `CLAUDE.md`「必须遵循」、`.github/workflows/build.yml` |
| GitHub 子模块上游 | `https://github.com/scylladb/seastar.git`、`https://github.com/ConorWilliams/libfork.git` | `.gitmodules:1-7` |
| apt 系统包 | ninja-build、clang 及 Seastar 系统依赖（经 install-dependencies.sh） | `.github/workflows/build.yml:17-19`、`README.md:52-53` |
| GitHub 访问加速 | 按 `github.com` → `kkgithub.com` → `ghfast.top` 顺序尝试 | `README.md:11`、`CLAUDE.md`「Git 访问」 |

### 2) Data Stores

无数据库。持久化仅为本地文件：

- **CSV 输出**: `output/<program>.csv`，每行 `<start>-<end>,<core_id>,<prime1>,<prime2>,...`（`README.md:133`）
- **构建产物**: `build/release|debug/`
- 无日期字段；数值为 uint64 区间与素数

### 3) Secrets and Credentials Handling

- Git 推送凭据: 环境变量 `GIT_USERNAME` + `GIT_PASSWORD`，**禁止写入仓库**（`CLAUDE.md`「Git 认证」）
- 禁止 `http.sslVerify=false`（`CLAUDE.md`「必须遵循」）
- 程序本身不消费任何凭据（无网络 I/O）

### 4) Reliability and Failure Behavior

- 无外部服务依赖 → 运行时无重试/熔断需求
- 子进程失败: `prime_bench` 的 `runProgram` 记录耗时为 0 的用例在对账时被豁免（`src/prime_bench.cpp:183`），不中断整轮
- 脚本失败: `set -euo pipefail` 快速失败（`scripts/verify_sieve.sh:4`）
- 网络仅在 clone/CI 阶段 involved；镜像回退顺序见上表

### 5) Observability for Integrations

- 无 APM/指标管道
- 可观测手段: 程序 stdout 中文报告（素数总数/耗时/最快框架）、Seastar logger（`-l` 级别）、CSV 产物留档、`scripts/check_environment.sh` 的 `[OK]/[WARN]/[FAIL]` 清单

### 6) Evidence

- `.gitmodules`（上游集成）
- `.github/workflows/build.yml`（CI 集成与依赖安装）
- `README.md:8-13`（远程与镜像顺序）
- `src/prime_bench.cpp:174-190`（子进程结果处理）
- `scripts/check_environment.sh`（环境探测输出格式）
