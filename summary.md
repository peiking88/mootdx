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


## 2026-05-08 续 — save_to_csv 改用 dma_write 批量写法

### 优化实施

参考 `kimi_seastar_prime.cpp` 与 CLAUDE.md 中关于「`open_file_dma()` + `dma_write()` 批量 + `seastar::repeat` 流式」的项目约定，重写 `save_to_csv`：

- **裸 `file::dma_write`** 替代 `file_output_stream` 包装层：省去内部状态机/连续协程开销
- **双缓冲流水线**：buf_a 填充时 buf_b 的 `dma_write` 在飞行；通过 `in_flight.get()` 在切换时等待对面缓冲
- **直接写入对齐 DMA 缓冲**：`fast_uint64_to_str` 写入 stack tmp[20]，再 `put_bytes` 跨边界切片拷贝到主缓冲；省掉 `std::string` 中间层
- **末尾不足一块**：填零至 `disk_write_dma_alignment()` 倍数后写入，再 `f.truncate(real_total)` 恢复实际大小

### 排错记录

第一版 `flush_full` 无条件写整个 `kBufSize`，但 `put_u64` 在 `cur_used + 20 > kBufSize` 时也调用 flush（此时 `cur_used` < `kBufSize`），残余字节为零，导致 CSV 中漏入 NUL 字节，sort 后多出 15 个伪素数。修复：flush 仅在 `cur_used == kBufSize` 时触发；`put_u64`/`put_bytes` 通过循环切片处理跨边界写入。

### 验证结果

| 场景 | 总耗时（前版本） | 总耗时（dma_write 版） | 一致性 |
|---|---|---|---|
| `-t 32 -n 5000000 -c 16` | ~103 ms | **~98 ms** | 文件 md5 与 minimax 完全一致 ✓ |
| `-t 64 -n 10000000 -c 16` | — | 370 ms（CSV 311MB ≈ 1 GB/s）| 文件大小 326490356 字节与 minimax 完全一致 ✓ |

CSV I/O 时间从 ~91ms 降至 ~86ms（~5% 改善）。改善幅度有限的原因：`file_output_stream` 内部已经做了相同的 4MB dma_write 批量化，主要开销在 CPU 侧的字符串构建上，已逼近 NVMe 顺序写带宽。

