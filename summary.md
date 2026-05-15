# 工作摘要

**时间:** 2026-05-15 13:30:00

## 变更概要
移除新浪交易日历接口（holidays/holiday2），统一使用通达信官网数据源；修复 holiday() 在 pandas 新版下 isin 匹配失效的 bug。

## 变更文件
- `mootdx/utils/holiday.py` — 删除 holidays()/holiday2() 及 JS_DECODE，修复 isin → 直接比较
- `mootdx/utils/holiday.js` — 删除（新浪数据解密脚本，不再需要）
