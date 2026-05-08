# 工作摘要

## 2026-05-08 — 调用 cpp-low-latency 技能评审并优化 gemma4_seastar_prime

### 评审发现（按严重度）

| 编号 | 严重度 | 问题 | 位置 |
|---|---|---|---|
| 1 | P1 | 计时混入 I/O，让纯计算延时不可见，误判 10× | 原 `:126-159` |
| 2 | P1 | 每任务一次 `submit_to + seastar::async`，跨 shard 消息 O(任务数) | 原 `:128-142` |
| 3 | P1 | 跨 shard 内存释放：远 shard 分配的 vector 在 shard 0 析构 | 原 `:144-150` |
| 4 | P2 | 死代码：`logger gemmalog` 声明但从未使用 | 原 `:27` |
| 5 | P3 | `TaskResult` 缺 `noexcept` move ctor，STL 容器可能退化为复制 | 原 `:34-38` |

### 优化实施（迭代 1）

- **每核 1 次 submit_to + 内部 for 循环**：调度开销由 O(num_tasks) 降至 O(num_cores)。32 任务 16 核场景下 submit_to 调用从 32 次降至 16 次。
- **保留 Round-Robin 静态分发语义**：核 c 处理任务 i = c, c+N, c+2N, ...（cerebrum 已记录此身份不可改）。
- **拆分计时**：新增 `计算耗时:` 行（纯计算 wall clock），保留 `总耗时:` 行（含 CSV I/O）。
- **TaskResult 加 noexcept move**：避免 STL reallocation 时退化为 copy。
- **删除未使用 logger**。

### 验证结果（`-t 32 -n 5000000 -c 16`）

| 指标 | 优化前 | 优化后 |
|---|---|---|
| 总耗时 | ~100 ms | ~103 ms |
| 计算耗时（拆出） | 不可见 | 12 ms |
| 素数总数 | 8974458 | 8974458 ✓ |
| 与 minimax 素数集合一致 | 未验证 | 完全一致 ✓ |

主要价值：让真实计算耗时（≈12ms，与 minimax 的 10ms 同量级）变得可观测；CSV I/O 占大头（~90ms）已暴露为后续优化目标。

