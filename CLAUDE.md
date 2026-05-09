# mootdx 项目规范

## Git 认证

使用 `GIT_USERNAME` + `GIT_PASSWORD` 环境变量进行认证。
推送时拼接认证 URL，完成后恢复无 token 地址：

```bash
git remote set-url origin "https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/peiking88/mootdx.git"
git push origin master
git remote set-url origin "https://github.com/peiking88/mootdx.git"
```

- 远程仓库：`https://github.com/peiking88/mootdx.git`
- 镜像仓库：`https://kkgithub.com/peiking88/mootdx.git`

## Git 访问

推送/拉取时依次尝试以下地址：

1. `https://github.com`（origin，双向）
2. `https://kkgithub.com`（mirror，双向）
3. `https://ghfast.top/https://github.com`

当 origin 操作失败时，使用 mirror 远程仓库作为备用。

## 域名替换

所有对 `https://bgithub.xyz` 的引用统一替换为 `https://github.com`。

## 语言规范

- 工作过程使用中文
- 生成文档使用中文
- 提交信息（commit message）使用中文
- README 及其他文档使用中文
