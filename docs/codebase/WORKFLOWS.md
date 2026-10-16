# Workflow Blueprints

## Core Sections (Required)

### 1) Workflow Catalog

| # | 工作流 | 触发 | 关键文件 |
|---|---|---|---|
| WF1 | 跑一轮完整基准 | 性能对比/回归确认 | `src/prime_bench.cpp`、`build.sh` |
| WF2 | 新增一个素数调度变体 | 实验新分发策略 | `src/`、`CMakeLists.txt`、`README.md`、`docs/api.md`、`prime_bench` |
| WF3 | 修改共享筛法内核 | 算法优化/缺陷修复 | `src/prime_sieve.hpp`、`scripts/verify_sieve.sh` |
| WF4 | 环境初始化/接手 | 新机器、新协作者 | `scripts/check_environment.sh`、`.gitmodules` |
| WF5 | 发布提交 | 每次提交前 | `summary.md`、`docs/api.md`、`README.md`、`VERSION` |

### 2) Workflow Traces

**WF1 跑基准**（全路径）：
1. `./build.sh -r -j $(nproc)` → cmake+Ninja 全量构建（`build.sh:118-124`）
2. `./build/release/prime_bench -t 32 -n 100000 -c 32` → mkdir output/（`prime_bench.cpp:265-268`）
3. 依序 fork+execvp 10 用例 `[1/10]`…`[10/10]`（`:272-324`）；每个被测程序内部走 ARCHITECTURE.md「素数程序数据流」
4. 对账：非 sequence 用例的素数总数 vs 基线（`:174-190`）；不一致 → `✗`，一致 → `✓ 通过`
5. 输出：排行表 + 最快框架；CSV 落 `output/`

**WF3 改筛法内核**（护栏闭环）：
1. 编辑 `src/prime_sieve.hpp`（唯一算法落点）
2. `scripts/verify_sieve.sh`：重建 glm5_seastar_prime → 跑 2×10⁹ → 断言 98,222,287（`verify_sieve.sh:14-25`）
3. 建议加跑 `prime_bench` 验证 10 程序对账仍 `✓`（共享内核波及全部程序）

### 3) Layer Implementation Patterns

| 模式 | 实现 | 证据 |
|---|---|---|
| 任务分发（8 变体） | atomic 计数器 / 集中队列+submit_to / mutex 队列 / seastar::async / 蛇形静态 Round-Robin | 各 `src/*_seastar_prime.cpp` 头注释 |
| CPU 密集卸载 | Seastar 侧 `seastar::async`/线程上下文执行筛法，避免阻塞 reactor | `src/dk4_seastar_prime.cpp:3-4` |
| 高吞吐文件写 | 裸 dma_write + 4MiB 双缓冲流水线（gemma4 范式） | `src/gemma4_seastar_prime.cpp:43-82` |
| 子进程编排 | fork+execvp + stdout 解析 + rename 归档 | `src/prime_bench.cpp:43-73,274` |

### 4) Error Handling Patterns

| 场景 | 模式 | 证据 |
|---|---|---|
| 黄金值不符 | `exit 1` 快速失败 | `scripts/verify_sieve.sh:22-25` |
| 环境缺失 | `[FAIL]` 计数，汇总后非零退出 | `scripts/check_environment.sh:26-30` |
| 非致命系统调用 | `std::cerr << "警告: …"` 继续（mkdir EEXIST） | `src/prime_bench.cpp:265-268` |
| 被测程序失败 | duration==0 豁免对账，不中断整轮 | `src/prime_bench.cpp:183` |
| Retry/circuit-breaker | 无（本地无外部依赖） | — |

### 5) Implementation Templates

**新增素数变体（WF2）改动清单**——顺序即依赖序：
1. `src/<name>_seastar_prime.cpp`：复制最接近的现有变体（如 `longcat_seastar_prime.cpp`），改分发逻辑；头三行注释（程序名/工作模式/接口兼容）；`#include "prime_sieve.hpp"`；统一 CLI `-t/-n/-o/-c`；stdout 打 `素数总数:` 行
2. `CMakeLists.txt`：`add_executable` + `target_link_libraries(Seastar::seastar 或 libfork::libfork)`
3. `src/prime_bench.cpp`：追加 `[N+1/10→N+1]` 用例块（runProgram + rename/`-o`）
4. `README.md` 程序表 + `docs/api.md` 适用程序列表 + `VERSION` 次版本号
5. 验证：`./build.sh -r <name>` → 单跑 → `prime_bench` 对账 `✓`

**修改共享内核（WF3）**：`src/prime_sieve.hpp` → `scripts/verify_sieve.sh` → `prime_bench` 对账。

**发布（WF5）**：更新 `summary.md` → `docs/api.md`/`README.md` → `VERSION`（功能升次版本/缺陷升三级版本，主版本先问用户）→ 检查无敏感信息/external//sslVerify 配置 → 激活虚拟环境跑测试（现实约束：见 TESTING.md）→ 提交。

### 6) Common Pitfalls

- **`-c` 语义双关**: Seastar 程序 `-c` = shard 数（框架 `--smp`），libfork/sequence 程序 `-c` = 线程数——bench 传参时两套 `base_args`/`seastar_args` 分开构造即为此（`src/prime_bench.cpp:273,285`）
- **输出文件名双轨**: libfork/sequence 程序输出在 cwd 再 rename 到 output/，Seastar 程序直接 `-o output/...`（`:274-324`）——新变体选 Seastar 路径更简
- **忘跑 verify_sieve**: 改 `prime_sieve.hpp` 不跑黄金值，错误会静默扩散到全部 12 个程序（共享单点）
- **编译警告被吞**: `-w` 全局生效（`CMakeLists.txt:225`），新代码的警告不会显示——需自行静态审查
- **external/ 红线**: 任何"顺手修复"上游头文件的冲动都违反仓库硬规约

### 7) Evidence

- `src/prime_bench.cpp:265-324`（WF1 全路径）
- `scripts/verify_sieve.sh`（WF3 护栏）
- `README.md:95-112`（CLI 契约与 `-c` 语义）
- `CLAUDE.md`「提交前要求」（WF5）
- git log `5284036`/`249786e`（WF2 的两次真实落地：longcat、gemma4 加入套件）
