# Architecture

## Core Sections (Required)

### 1) Architectural Style

**扁平单层可执行矩阵 + 共享算法内核**。没有分层（无 controller/service/repo），没有库目标——12 个独立 main 围绕同一个 `prime::segmented_sieve` 实现，唯一结构变量是**任务调度模式**。项目的架构目的即对比本身：算法恒定（`src/prime_sieve.hpp`），调度为实验变量。

两条执行轴线：

- **Seastar 轴**（share-nothing，每核一个 reactor，shard 间通 `submit_to`/`smp`）：8 种分发策略
- **libfork 轴**（线程 + fork-join/工作窃取）：2 种
- 外加顺序基线（`sequence_prime`）与编排器（`prime_bench`）

### 2) System Flow

**素数程序数据流**（以 minimax_seastar 为例，各变体仅分发步骤不同）：

```
CLI 参数 (-t/-n/-o/-c)                     src/minimax_seastar_prime.cpp main
  → 任务区间生成（t 个 [start,end)，每段 n）
  → 分发到各 shard（atomic/queue/mutex/静态 Round-Robin 之一）   ← 唯一实验变量
  → 各核独立调用 prime::segmented_sieve                          src/prime_sieve.hpp
  → per-shard 结果聚合（submit_to(0) 或结果数组）
  → 异步 DMA 写 CSV (open_file_dma + dma_write)                  避免阻塞 reactor
  → stdout 打印 "素数总数: N" + 计算耗时（供 prime_bench 采集）
```

**基准编排流**（`src/prime_bench.cpp`）：

```
prime_bench main → 依序 fork+execvp 10 个被测程序（[1/10]…[10/10]）
  → 采集各自 stdout 的素数总数与耗时                    src/prime_bench.cpp:174-190
  → 与 sequence_prime 结果对账（结果一致性校验）
  → 输出排行表 + 最快框架
```

### 3) Layer/Module Responsibilities

| 模块 | 职责 | 不负责 |
|---|---|---|
| `src/prime_sieve.hpp` | 素数算法（分段筛法、位压缩、字级标记） | 并行、I/O、CLI |
| 各 `*_prime.cpp` | 任务切分、调度分发、结果聚合、CSV 写、CLI | 算法细节（委托 sieve） |
| `src/prime_bench.cpp` | 编排、计时、对账 | 计算本身 |
| `src/big_file_splitter.cpp` | 大文件并行分割（独立功能） | 素数域 |
| `scripts/verify_sieve.sh` | 算法黄金值校验（π(2×10⁹)=98,222,287） | — |
| `scripts/check_environment.sh` | 环境完整性 | — |

### 4) Reused Patterns

- **统一 CLI 契约**: 全部素数程序 `-t/-n/-o/-c`（`docs/api.md`「通用约定」），保证 bench 可参数化驱动
- **标准输出协议**: `素数总数: N` 解析行（`README.md:164`），程序间唯一通信契约
- **异步 DMA I/O**: Seastar 程序统一 `open_file_dma()` + `dma_write()`；gemma4 进一步裸 dma_write + 4MiB 双缓冲流水线（`src/gemma4_seastar_prime.cpp:43-82`、commit `87b939a`）
- **头三行注释模式**: 程序名 / 工作模式 / 接口兼容性声明（如 `src/longcat_seastar_prime.cpp:1-3`）
- **fork+execvp 替代 popen**: 避免 shell 注入（`src/prime_bench.cpp:3`）

### 5) Known Architectural Risks

- **集中式模式的 core 0 瓶颈**是已知实验结论而非缺陷（`README.md:243-251` 对比表：glm5 "core 0 可能成为瓶颈"）
- **`prime_bench` 串行运行 10 用例**：总耗时≈各程序之和；对 benchmark 属可接受（隔离测量），非待优化项
- **stdout 协议脆弱**: bench 依赖中文 `素数总数:` 文案解析，程序输出文案变化会静默破坏对账 `[TODO: 是否加退出码/机器可读协议]`
- **无进程级失败重试**: `runProgram` 返回后仅对 duration>0 做对账豁免（`src/prime_bench.cpp:183`），被测程序崩溃的处理路径未显式定义

### 6) Evidence

- `src/prime_sieve.hpp:1-15`（共享内核 + 边界声明）
- `src/prime_bench.cpp:43-73`（fork+execvp）、`:174-190`（对账）、`:272-324`（10 用例）
- `src/gemma4_seastar_prime.cpp:162`（蛇形 Round-Robin）、`:43-82`（双缓冲 DMA）
- `README.md:243-251`（两实现对比表）
- 各程序头注释（`src/*.cpp:1-5`）
