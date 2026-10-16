# Codebase Concerns

## Core Sections (Required)

### 1) Top Risks (Prioritized)

- **R-1（高）规范-现实断裂: 测试要求 vs 零测试**。`CLAUDE.md`「测试」与 `docs/project-rules.md`「验收规范」要求覆盖率 >80%、单元+集成测试全过才算完成；现实是 `tests/` 为空、CMake 无任何测试基础设施。每次按规范声称"测试通过"都无事实支撑。
- **R-2（高）规范-现实断裂: 中断续跑承诺未实现**。`README.md:107,112` 与 `docs/api.md`「通用约定」声称"批处理长任务必须支持中断重试和续跑"，但 `grep -rn "resume|续跑|断点|checkpoint" src/` 零命中——长跑（如 verify_sieve 的 2×10⁹）中断只能从头重来。
- **R-3（中）`prime_bench` stdout 协议脆弱**。对账依赖中文文案 `素数总数:` 的 stdout 解析（`src/prime_bench.cpp:174-190`）；任一程序输出文案微调即静默破坏一致性校验。且被测程序崩溃路径只以 duration==0 豁免（`:183`），无显式失败报告。
- **R-4（中）全局关闭编译警告**。`CMakeLists.txt:225` 追加 `-w -Wno-error` 对全部 12 个目标生效——外部依赖的警告噪音被连带压制自身代码的真实警告（未初始化、签名不匹配等）也无从发现。与"第三方组件不计入"的本意可用 target 级 `target_compile_options` 外部目标隔离替代。
- **R-5（低）`output/` 磁盘堆积**。约 982MB 历史 CSV（最大单文件 `glm5_seastar_prime.csv` ≈976MB）滞留工作区；git 已忽略但磁盘无清理机制。

### 2) Technical Debt

- `cfg/` 空目录：规范模板要求配置文件目录，实际全部配置走 CLI，目录仅 `.gitkeep` 占位——要么落地用途要么从规范中除名 `[ASK USER]`
- README 示例输出块（`README.md:191-216`）仍是 5 框架旧形态，与现 10 用例输出不符（本批已修头注释与路径块，此项未动——刷新需真实运行 prime_bench 取输出）
- `docs/iotune-manual.md` 为 Seastar iotune 上游手册留档，与本项目工作流无引用关系

### 3) Security Concerns

- `prime_bench` 用 `fork+execvp` 而非 `popen`，明确规避 shell 注入（`src/prime_bench.cpp:3`）——正面
- 无网络输入面、无凭据落盘（凭据仅走环境变量）、CI 未禁用 sslVerify——无已知风险项
- 子进程参数全部来自 CLI 数字/路径，无未验证注入点（`-o` 路径由使用者自控，本地工具可接受）

### 4) Performance and Scaling Concerns

- 集中式队列模式（glm5/kimi/dk4/longcat）的 core 0 / 锁瓶颈是**设计实验变量**而非缺陷（`README.md:243-251`）——修复它等于消灭对比对象
- `verify_sieve.sh` 固定 `-t 10000 -n 200000`（2×10⁹ 全区间）单次约数百毫秒~秒级，可接受
- 真实瓶颈记录：Seastar 程序在 README 示例中比 libfork 慢一个数量级（441ms vs 33ms），属框架启动/reactor 开销，为已知对比结论

### 5) Fragile/High-Churn Areas

- 近 90 天高变更文件（扫描输出 HIGH-CHURN）：全部 `src/*.cpp` 均为 1 次提交（新增型仓库，churn 低）；`README.md`、`VERSION`、`docs/api.md` 每次提交必动（规约要求），变更频率高但为文档面
- 共享内核 `src/prime_sieve.hpp` 是**单点**：12 个程序的正确性全押在它上面——已有黄金值校验护栏（verify_sieve.sh），风险受控

### 6) `[ASK USER]` Questions

1. 测试规范（>80% 覆盖率、单测+集成）是否要落地？若落地，选型建议 GTest + CTest + gcovr（R-1）
2. 「中断重试和续跑」承诺：是为素数批处理实现 checkpoint（已完成区间落盘+跳过），还是从 README/api.md 规范中移除该承诺？（R-2）
3. `-w` 全局关警告：改为仅对 `external/` 目标豁免、自身代码恢复 `-Wall -Wextra`？（R-4）
4. `cfg/` 空目录的去留：保留占位、落地真实配置（如默认参数文件）、还是移除？
5. 新增素数变体是否延续 LLM 别名命名惯例？

### 7) Evidence

- `CLAUDE.md`「测试」/「验收标准」、`docs/project-rules.md`「测试规范」（R-1 规范侧）
- `find tests -type f` → `.gitkeep`；`CMakeLists.txt` 无 enable_testing（R-1 现实侧）
- `README.md:107,112`、`docs/api.md:7`（R-2 承诺侧）；grep 零命中（R-2 现实侧）
- `src/prime_bench.cpp:174-190`（R-3）
- `CMakeLists.txt:225`（R-4）
- `du -sh output/` → 982M（R-5）
- `README.md:191-216`（示例输出过时）
