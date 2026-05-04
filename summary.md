# 提交摘要

## 变更概述

本次变更主要完成以下工作：

1. **新增行情适配器层** - 新增 `hq_adapter.py`、`exhq_adapter.py`，封装 tdxpy/opentdx 双后端切换，优先使用 opentdx 新协议
2. **更新服务器列表** - 刷新全部 HQ/EX 行情服务器 IP，新增 HF 高级行情服务器组
3. **新增 TDX 目录查找器** - `tdxfinder.py` 自动发现通达信安装目录并解析 connect.cfg
4. **修复多个兼容性问题** - pandas fillna 废弃方法替换、北交所代码识别修复、空值处理修复
5. **恢复测试用例** - 移除已修复功能的 skip 标记，更新测试数据

## 修改文件

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| mootdx/hq_adapter.py | 新增 | 标准行情适配器 |
| mootdx/exhq_adapter.py | 新增 | 扩展行情适配器 |
| mootdx/tdxfinder.py | 新增 | TDX 安装目录查找 |
| mootdx/consts.py | 更新 | 服务器列表刷新，新增 HF_HOSTS |
| mootdx/config.py | 更新 | 集成 tdxfinder 自动发现 |
| mootdx/quotes.py | 更新 | 切换适配器，增加异常处理 |
| mootdx/server.py | 更新 | 切换适配器 |
| mootdx/financial/*.py | 更新 | 切换适配器，修复空值 Bug |
| mootdx/utils/__init__.py | 更新 | 修复北交所代码识别 |
| mootdx/tools/reversion.py | 更新 | 修复 pandas 废弃 API |
| tests/** | 更新 | 恢复测试，更新数据 |
