# 项目规范

## Git 规范

- 认证方式：使用 `GIT_USERNAME` + `GIT_PASSWORD` 环境变量。
- 远程仓库：`https://github.com/peiking88/mootdx.git`。
- Git 用户：
  - `user.name`: `peiking88`
  - `user.email`: `peiking88@users.noreply.github.com`
- 禁止把用户名、密码、令牌、Cookie、私钥、`.env` 等敏感信息提交到仓库。
- 禁止把 `http.sslVerify` 设为 `false`。
- 禁止提交 `external/` 内容。
- 所有旧 GitHub 镜像域名访问必须替换为 `https://github.com`。

## Git 访问顺序

访问 GitHub 时按下面顺序尝试：

| 顺序 | 地址 | 用途 |
|---|---|---|
| 1 | `https://github.com` | 双向，拉取和推送 |
| 2 | `https://kkgithub.com` | 双向，拉取和推送 |
| 3 | `https://ghfast.top/https://github.com` | 下载加速 |

推送前必须确认提交内容不包含敏感信息。

## 提交前流程

每次提交前必须执行：

1. 更新 `summary.md`，用中文总结当前工作。
2. 更新 `docs/api.md` 和 `README.md`。
3. 设置版本号：
   - 新增功能：升次版本号。
   - 修改缺陷：升三级版本号。
   - 升主版本号：必须先征求用户意见。
4. 运行敏感信息和禁用项检查。
5. 激活虚拟环境后运行测试。

## 语言规范

- 工作过程：中文。
- 生成文档：中文。
- 提交变更说明：中文。
- README：中文。
- 代码注释优先中文；已有英文上下文可保持一致，但新增项目文档必须中文。

## 编译规范

- 使用 Ninja 或 Make 时必须并行：
  - Ninja：`ninja -C build/release -j$(nproc)`
  - Make：`make -C build -j$(nproc)`
- 构建脚本默认使用 `$(nproc)` 作为并行度。
- 优先使用国内镜像下载软件、依赖包、模型和数据。

## 需求规范

- 批处理长任务必须支持：
  - `n` 参数，用于控制批量数量、任务数量或处理条数。
  - 中断重试。
  - 续跑，避免重复处理已完成任务。
- 路径类参数必须可配置，例如输入路径、输出路径、缓存路径、配置路径、模型路径和数据路径。
- 禁止把路径硬编码进业务逻辑。

## 代码库分析规范

- 适配依赖库新版本前，必须先阅读该依赖的新版本 API 文档。
- 修改 Seastar、libfork 等依赖相关逻辑前，优先查阅对应官方文档或仓库内文档。

## 禁止事项

- 不修改 `external/` 下的源文件。
- 不提交 `external/`。
- 不把 `http.sslVerify` 设为 `false`。
- 不跳过、不简化测试用例来制造通过结果。
- 不在提交中包含敏感信息。

## 测试规范

- 覆盖率目标：大于 80%。
- 用例不简化、不跳过。
- 覆盖真实测试和 mock 测试，非必要不 mock。
- 真实测试中如果返回数量大于 50，验证样本或总数。
- 第三方组件不计入覆盖率，不做单元测试。
- 先激活虚拟环境，再运行测试。

## 验收规范

- 阶段完成：所有单元测试通过后进入下一阶段。
- 全部完成：所有单元测试和集成测试通过。
- 初始化完成：必须运行 `scripts/check_environment.sh` 并报告环境完整性。

## 目录规范

项目固定使用以下一级目录：

```text
docs/
cfg/
src/
scripts/
tests/
output/
```

`external/` 只用于第三方依赖，不属于可修改业务目录。
