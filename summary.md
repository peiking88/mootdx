# 工作摘要

**时间:** 2026-05-09

## 变更概要
- 删除死代码 demjson.py（6320行，无引用）
- 删除 utils/adjust.py 中废弃的 to_adjust2() 函数
- StdQuotes 新增 get_factor() 方法，统一封装 Opentdx AdjustmentFactorCrawler
- 版本升级至 0.15.0

## 最近提交
```
0f5d5f5 解除 opentdx 循环依赖，内联常量定义并增强服务器发现兼容性
adcac09 同步项目配置、文档及杂项文件
04d3489 按规范整理项目目录结构
f60089e 更新 API 文档：新增复权K线、数据校验、变更日志
cb4c56a 升级版本号至 0.14.0 — 增强功能并下沉通用能力
```
