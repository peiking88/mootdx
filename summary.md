# 工作摘要

**时间:** 2026-05-09

## 变更概要

- consts.py: 常量内联定义，解除对 opentdx 的硬依赖，避免循环导入
- server.py: 服务器列表支持 opentdx/tdxpy 动态合并，增强兼容性
- holiday.js: 代码格式整理
- 目录结构: 按规范整理，移除 src/ 包装，Python 包置于项目根
- 版本升至 0.14.1

## 测试结果

314 passed, 4 skipped in 138.93s
