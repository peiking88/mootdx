# iotune 用户手册

`iotune` 是 Seastar 自带的存储基准测试工具：用真实读写探测目标盘的 IOPS 与带宽上限，输出 `io_properties.yaml` 给 Seastar 程序在启动时加载，省去每次启动现场探测（也就消除日志中那条 `IO queue was unable to find a suitable maximum request length` 的 INFO 提示）。

适用场景：

- 想把 Seastar 的 IO 调度参数固化下来，启动更快、行为更稳定。
- 程序有较多磁盘读写（日志、CSV、DMA 输出），想拿到接近硬件极限的吞吐。
- 在新机器、换盘后做一次磁盘画像归档。

---

## 1. 可执行文件位置

构建 Seastar 后，二进制位于：

```
external/seastar/build/release/apps/iotune/iotune
```

如果尚未构建，单独构建该 app：

```bash
cd external/seastar
./configure.py --mode=release --enable-apps
ninja -C build/release apps/iotune/iotune -j$(nproc)
```

> 本项目策略是**不修改 `external/`**，仅在其下编译产物。

---

## 2. 命令行参数

| 参数 | 必需 | 说明 |
|---|---|---|
| `--evaluation-directory <path>` | 是 | iotune 在该目录创建临时文件做读写测试。**必须与程序后续真正使用的输出目录在同一个挂载点（同一块盘）**，否则测出来的参数对不上 |
| `--properties-file <path>` | 否 | 输出 yaml 路径，默认 `/etc/seastar/io_properties.yaml`（写系统目录通常需 sudo） |
| `--format <seastar\|envfile>` | 否 | 默认 `seastar`（yaml）。`envfile` 输出可被 shell `source` 的环境变量形式 |
| `--duration <秒>` | 否 | 单项测试时长，默认约 120s。盘越慢越要给足时间 |
| `--smp <N>` | 否 | 用几个 shard 跑测试，一般取物理核数 |
| `--io-complexity <N>` | 否 | 队列深度（并发请求数），高级调参用 |
| `--accuracy <0~1>` | 否 | 收敛精度，越高越准也越慢 |

> Seastar 通用参数（`--cpuset`、`--memory`、`--reserve-memory` 等）也可叠加，遵循 Seastar app 一贯约定。

---

## 3. 典型用法

### 3.1 给本项目 `output/` 做一次画像

```bash
mkdir -p /home/li/peiking88/starter/output

sudo ./external/seastar/build/release/apps/iotune/iotune \
    --evaluation-directory /home/li/peiking88/starter/output \
    --properties-file    /home/li/peiking88/starter/cfg/io_properties.yaml \
    --smp $(nproc)
```

测试持续约 **2~5 分钟**，期间会在 `output/` 下创建几 GB 的临时文件并自动删除。**确保磁盘有 ≥10GB 空闲**。

### 3.2 让 Seastar 程序使用画像文件

```bash
./build/release/kimi_seastar_prime \
    -t 32 -n 100000 -c $(nproc) \
    --io-properties-file /home/li/peiking88/starter/cfg/io_properties.yaml
```

或者放到默认路径（之后免参数）：

```bash
sudo mkdir -p /etc/seastar
sudo cp /home/li/peiking88/starter/cfg/io_properties.yaml /etc/seastar/
```

### 3.3 输出 envfile 形式（CI / 容器场景）

```bash
sudo ./external/seastar/build/release/apps/iotune/iotune \
    --evaluation-directory /home/li/peiking88/starter/output \
    --properties-file /tmp/seastar.env \
    --format envfile

source /tmp/seastar.env
./build/release/prime_bench -t 32 -n 100000 -c $(nproc)
```

---

## 4. 输出 yaml 示例

```yaml
disks:
  - mountpoint: /home/li/peiking88/starter/output
    read_iops: 412300
    read_bandwidth: 3221225472   # 3 GiB/s
    write_iops: 156000
    write_bandwidth: 1610612736  # 1.5 GiB/s
```

字段含义：

| 字段 | 单位 | 含义 |
|---|---|---|
| `mountpoint` | 路径 | 该项参数所属的挂载点 |
| `read_iops` / `write_iops` | 次/秒 | 小请求随机 IO 上限 |
| `read_bandwidth` / `write_bandwidth` | 字节/秒 | 大请求顺序带宽上限 |

> 多个挂载点会输出多条 `disks` 条目。Seastar 启动时按程序实际写入的路径匹配挂载点。

---

## 5. 常见坑与排错

| 现象 | 原因 | 解决 |
|---|---|---|
| `Permission denied` 写 `/etc/seastar/` | 默认输出路径需 root | 加 `sudo`，或把 `--properties-file` 指到用户目录 |
| `Not enough space` | 临时测试文件空间不够 | 清出 ≥10GB 空闲；或减少 `--smp` |
| 数值离谱 / 程序仍报警告 | 测试目录在 tmpfs / loop / 网络盘 | 换到真实数据盘的挂载点 |
| 容器/VM 内数值漂移大 | 宿主机其它 IO 干扰 | 关闭其它负载；或 `--duration 300` 拉长测试 |
| 仍打印 `unable to find suitable maximum request length` | 该盘延迟曲线本身平坦（NVMe / 虚拟盘） | **属正常**，可忽略；或调高日志等级 |
| iotune 自身一直挂着不退出 | 盘极慢或 `--accuracy` 太高 | 降低 `--accuracy`，或缩短 `--duration` |

---

## 6. 是否值得为本项目跑

| 工作负载 | 建议 |
|---|---|
| 仅本地跑 prime benchmark（CPU 密集） | **可不跑**。该日志不影响正确性，对结果数字也几乎无影响 |
| 想消除启动日志、获得稳定 IO 调度 | 跑一次，结果落到 `cfg/io_properties.yaml` |
| 程序根本不写磁盘 | 完全不用管 |
| 仅想压日志 | 加 `--default-log-level warn` 启动参数即可 |

简化做法（只想去掉警告，不做画像）：

```bash
./build/release/prime_bench -t 32 -n 100000 -c $(nproc) \
    --default-log-level warn
```

---

## 7. 与项目集成建议

- 画像文件统一放 `cfg/io_properties.yaml`，纳入 git（不含敏感信息）。
- 在 `scripts/` 下加封装脚本（可选），例如 `scripts/iotune.sh`：

  ```bash
  #!/usr/bin/env bash
  set -euo pipefail
  ROOT="$(cd "$(dirname "$0")/.." && pwd)"
  IOTUNE="$ROOT/external/seastar/build/release/apps/iotune/iotune"
  EVAL_DIR="$ROOT/output"
  OUT="$ROOT/cfg/io_properties.yaml"

  mkdir -p "$EVAL_DIR" "$(dirname "$OUT")"
  sudo "$IOTUNE" \
      --evaluation-directory "$EVAL_DIR" \
      --properties-file "$OUT" \
      --smp "$(nproc)"
  ```

- 程序启动统一加 `--io-properties-file cfg/io_properties.yaml`，或写入 `/etc/seastar/io_properties.yaml` 让所有 Seastar 程序自动加载。

---

## 8. 参考

- Seastar 源码：`external/seastar/apps/iotune/`
- Seastar IO 调度文档：`external/seastar/doc/io_scheduler.md`（如存在）
- 本项目相关：`src/kimi_seastar_prime.cpp`（`output_results()` 中的 `dma_write` 用法）
