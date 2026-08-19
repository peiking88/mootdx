# API 文档

本文档记录当前项目可执行程序的命令行接口。新增或修改参数时，必须同步更新本文档和 `README.md`。

## 通用约定

- 路径类参数必须可配置。
- 长任务必须支持 `n` 参数、中断重试和续跑。
- Seastar 程序使用 `-c` 或 `--smp` 控制核心数。
- 输出文件默认写入 `output/` 目录，也可用 `-o` 显式指定路径。

## 素数计算程序

适用程序：

- `glm5_seastar_prime`
- `minimax_seastar_prime`
- `sonnet46_seastar_prime`
- `kimi_seastar_prime`
- `dk4_seastar_prime`
- `gemma4_seastar_prime`
- `longcat_seastar_prime`
- `glm5_libfork_prime`
- `minimax_libfork_prime`
- `sequence_prime`

| 参数 | 含义 | 默认值 |
|---|---|---|
| `-t <N>` | 任务总数 | 程序内默认值 |
| `-n <N>` | 每个任务的区间大小 | 程序内默认值 |
| `-c <N>` | 核心数或线程数 | 程序内默认值 |
| `-o <PATH>` | 输出 CSV 文件路径，Seastar 程序支持 | 程序名派生 |

示例：

```bash
./build/release/minimax_seastar_prime -t 20 -n 100000 -c 4 -o output/minimax.csv
./build/release/sequence_prime -t 20 -n 100000 -c 4
```

## `prime_bench`

多实现性能基准测试程序。

| 参数 | 含义 | 默认值 |
|---|---|---|
| `-t <N>` | 任务总数 | 4 |
| `-n <N>` | 每个任务的区间大小 | 100000 |
| `-c <N>` | 线程数或核心数 | 4 |

示例：

```bash
./build/release/prime_bench -t 32 -n 100000 -c 32
```

## `big_file_splitter`

大文件并行分割程序。

| 参数 | 含义 | 默认值 |
|---|---|---|
| `--input <PATH>` | 输入文件路径 | 必填 |
| `-c <N>` | 并发或分片相关参数 | 程序内默认值 |
| `-m <N>` | 分片大小相关参数 | 程序内默认值 |
| `--memory-pct <N>` | 可用内存比例 | 程序内默认值 |

示例：

```bash
./build/release/big_file_splitter --input input.dat -m500 -c5 --memory-pct 1.0
```

## 变更要求

新增 CLI 参数时必须说明：

- 参数名和短参数。
- 默认值。
- 是否为路径类参数。
- 是否影响中断重试和续跑。
- 是否影响测试样本数量或覆盖率。
