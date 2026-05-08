# Cerebrum

> OpenWolf's learning memory. Updated automatically as the AI learns from interactions.
> Do not edit manually unless correcting an error.
> Last updated: 2026-05-08

## User Preferences

<!-- How the user likes things done. Code style, tools, patterns, communication. -->

## Key Learnings

- **Project:** starter
- **Description:** 高性能C++并行计算项目，基于Seastar框架，支持多种并行计算框架的性能对比。
- **共享素数筛法**: 所有素数计算器应调用 `src/prime_sieve.hpp` 里的 `prime::segmented_sieve(start, end_exclusive)` 与 `util::fast_uint64_to_str`，避免各自实现试除法/stringstream
- **命名空间冲突**: `seastar` 里有 `seastar::util`，若 `using namespace seastar;` 后再调项目的顶层 `util::xxx` 会二义；需用 `::util::` 明确限定
- **Seastar submit_to 中做 CPU 密集工作**: 同步 lambda 会阻塞 reactor 及同核其他协程；把大块计算封进 `seastar::async([]{ ... })` 切到独立线程栈更稳妥
- **prime_bench 接入流程**: 新实现需 (1) 支持 `-t/-n/-o` 与 Seastar 框架参数；(2) 打印"素数总数: N"一行；(3) 在 `prime_bench.cpp` [N/M] 步中加入，并用 `sed` 批量修正前面所有 `[i/old]` 编号
- **gemma31b 身份**: 在 prime_bench 中归为 "Seastar Round-Robin 分发"（任务 i 投给 core i%num_cores），是静态分发的基线；不要把它改成工作窃取——那会变成 minimax 的职能


- **Seastar 每任务 submit_to 反模式**: 用 `for(i in tasks) submit_to(i%N, ...)` 让 driver 发出 O(任务数) 跨 shard 消息；改为 `for(c in cores) submit_to(c, [] { for i=c,c+N,... })` 后降至 O(核数)，gemma4 已采用。Round-Robin 静态分发语义不变。
- **gemma4 蛇形 Round-Robin**: gemma4 从简单模取余改为蛇形分发（偶数轮正向、奇数轮反向），每个 core 自动配对密集+稀疏区间，解决低编号 core 负载过高问题。仍是静态分发（非工作窃取），保持 gemma4 身份。
- **gemma4/分发型 prime 计时陷阱**: 用 `start_time` 到 save_to_csv 完成测量会把 ~90ms 的 CSV I/O 算进"耗时"，掩盖纯计算只有 ~12ms。新实现要拆分 `计算耗时:` 与 `总耗时:` 两行。

## Do-Not-Repeat

<!-- Mistakes made and corrected. Each entry prevents the same mistake recurring. -->
<!-- Format: [YYYY-MM-DD] Description of what went wrong and what to do instead. -->
- [2026-05-08] gemma31b 性能坑：不要用 `is_prime` 试除法做批量素数计算。n≥2e9 时 900× 慢于分段筛法。统一调 `prime::segmented_sieve`。
- [2026-05-08] 不要 `using namespace seastar;` 后再裸写 `util::fast_uint64_to_str`，会与 `seastar::util` 冲突。写成 `::util::fast_uint64_to_str`。


## Decision Log

<!-- Significant technical decisions with rationale. Why X was chosen over Y. -->
