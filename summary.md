# 工作摘要

**时间:** 2026-05-09 12:21:55

## 变更概要
```
 .coveragerc                                       |   0
 .drone.yml                                        |   2 +-
 .github/workflows/django.yml                      |   0
 .pre-commit-config.yaml                           |  38 +-
 .readthedocs.yaml                                 |   4 +-
 CLAUDE.md                                         |   9 +-
 Dockerfile                                        |   0
 Makefile                                          |   3 -
 README.md                                         |  33 ++
 docs/api/extras.md                                |   2 +-
 docs/faq/py_mini_racer.md                         |   0
 docs/history.md                                   | 140 +++---
 docs/img/todo.md                                  |   7 +-
 docs/setup.md                                     |   1 -
 docs/todo.md                                      |   3 +-
 mkdocs.yml                                        |  32 +-
 mootdx/__main__.py                                |  12 +-
 mootdx/cache/__init__.py                          |   0
 mootdx/cache/compat.py                            |   0
 mootdx/cache/file.py                              |   0
 mootdx/cache/timed.py                             |   0
 mootdx/cache/timer.py                             |   0
 mootdx/config.py                                  |   0
 mootdx/contrib/__init__.py                        |   0
 mootdx/contrib/adjust.py                          |   0
 mootdx/exceptions.py                              |   0
 mootdx/financial/__init__.py                      |   0
 mootdx/financial/base.py                          |   0
 mootdx/financial/financial.py                     |   0
 mootdx/logger.py                                  |   0
 mootdx/tools/DownloadTDXCaiWu.py                  |   0
 mootdx/tools/__init__.py                          |   0
 mootdx/tools/tdx2csv.py                           |   0
 mootdx/utils/__init__.py                          |   0
 mootdx/utils/adjust.py                            |   0
 mootdx/utils/demjson.py                           |   0
 mootdx/utils/factor.py                            |   0
 mootdx/utils/holiday.js                           | 568 ++++++++++++----------
 mootdx/utils/holiday.py                           |   0
 mootdx/utils/pandas_cache.py                      |   0
 mootdx/utils/timer.py                             |   0
 mootdx/version.py                                 |   0
 poetry.lock                                       |   0
 scripts/fabfile.py                                |   0
 summary.md                                        |  12 +-
 tests/__init__.py                                 |   0
 tests/cache/test_file.py                          |   0
 tests/conftest.py                                 |   0
 tests/financial/__init__.py                       |   0
 tests/financial/test_affairs.py                   |   0
 tests/fixtures/T0002/hq_cache/block_fg.dat        | Bin
 tests/fixtures/T0002/hq_cache/block_gn.dat        | Bin
 tests/fixtures/T0002/hq_cache/block_zs.dat        | Bin
 tests/fixtures/T0002/hq_cache/brkcomp.dat         |   0
 tests/fixtures/T0002/hq_cache/brkseat.dat         |   0
 tests/fixtures/T0002/hq_cache/code2gp.dat         |   0
 tests/fixtures/T0002/hq_cache/code2name.ini       |   0
 tests/fixtures/T0002/hq_cache/code2name_qq.ini    |   0
 tests/fixtures/T0002/hq_cache/ds_code.dat         | Bin
 tests/fixtures/T0002/hq_cache/ds_mrk.dat          | Bin
 tests/fixtures/T0002/hq_cache/ds_tinf.dat         | Bin
 tests/fixtures/T0002/hq_cache/funddiv.dat         | Bin
 tests/fixtures/T0002/hq_cache/fundhold.dat        | Bin
 tests/fixtures/T0002/hq_cache/fundinfo.dat        | Bin
 tests/fixtures/T0002/hq_cache/ggqqcode.txt        |   0
 tests/fixtures/T0002/hq_cache/hkblock.dat         |   0
 tests/fixtures/T0002/hq_cache/hkcwdata.dat        | Bin
 tests/fixtures/T0002/hq_cache/hkqxinfo.dat        | Bin
 tests/fixtures/T0002/hq_cache/hkqxinfo2.dat       | Bin
 tests/fixtures/T0002/hq_cache/hkxgsg.cfg          |   0
 tests/fixtures/T0002/hq_cache/hkzsinfo.cfg        |   0
 tests/fixtures/T0002/hq_cache/hqrule.dat          |   0
 tests/fixtures/T0002/hq_cache/hspy.dat            |   0
 tests/fixtures/T0002/hq_cache/importzs.cfg        |   0
 tests/fixtures/T0002/hq_cache/infoharbor_spec.cfg |   0
 tests/fixtures/T0002/hq_cache/itcomte.dat         | Bin
 tests/fixtures/T0002/hq_cache/jjblock.dat         |   0
 tests/fixtures/T0002/hq_cache/mgblock.dat         |   0
 tests/fixtures/T0002/hq_cache/mgcwdata.dat        | Bin
 tests/fixtures/T0002/hq_cache/mgqxinfo.dat        | Bin
 tests/fixtures/T0002/hq_cache/neednote.dat        |   0
 tests/fixtures/T0002/hq_cache/neeqcode.txt        |   0
 tests/fixtures/T0002/hq_cache/nscomte.dat         | Bin
 tests/fixtures/T0002/hq_cache/othersg.cfg         |   0
 tests/fixtures/T0002/hq_cache/profile.dat         | Bin
 tests/fixtures/T0002/hq_cache/pttab.dat           |   0
 tests/fixtures/T0002/hq_cache/relation.dat        | Bin
 tests/fixtures/T0002/hq_cache/sbblock.dat         |   0
 tests/fixtures/T0002/hq_cache/sh.tcu              | Bin
 tests/fixtures/T0002/hq_cache/sh.tfz              | Bin
 tests/fixtures/T0002/hq_cache/sh.th2              | Bin
 tests/fixtures/T0002/hq_cache/shm.tnf             | Bin
 tests/fixtures/T0002/hq_cache/shsz.tdf            | Bin
 tests/fixtures/T0002/hq_cache/spblock.dat         |   0
 tests/fixtures/T0002/hq_cache/specallzt.txt       |   0
 tests/fixtures/T0002/hq_cache/sz.tcu              | Bin
 tests/fixtures/T0002/hq_cache/sz.tfz              | Bin
 tests/fixtures/T0002/hq_cache/sz.th2              | Bin
 tests/fixtures/T0002/hq_cache/szm.tnf             | Bin
 tests/fixtures/T0002/hq_cache/szqqcode.txt        |   0
 tests/fixtures/T0002/hq_cache/tdxadr.cfg          |   0
 tests/fixtures/T0002/hq_cache/tdxbjmore.cfg       |   0
 tests/fixtures/T0002/hq_cache/tdxbk.cfg           |   0
 tests/fixtures/T0002/hq_cache/tdxdszs.cfg         |   0
 tests/fixtures/T0002/hq_cache/tdxhy.cfg           |   0
 tests/fixtures/T0002/hq_cache/tdxmgag.cfg         |   0
 tests/fixtures/T0002/hq_cache/tdxpkmore.cfg       |   0
 tests/fixtures/T0002/hq_cache/tdxsbzs.cfg         |   0
 tests/fixtures/T0002/hq_cache/tdxstat.cfg         |   0
 tests/fixtures/T0002/hq_cache/tdxzs.cfg           |   0
 tests/fixtures/T0002/hq_cache/tdxzs3.cfg          |   0
 tests/fixtures/T0002/hq_cache/tdxzsbase.cfg       |   0
 tests/fixtures/T0002/hq_cache/tend_std.cfg        |   0
 tests/fixtures/T0002/hq_cache/tipinfo.dat         |   0
 tests/fixtures/T0002/hq_cache/ukblock.dat         |   0
 tests/fixtures/T0002/hq_cache/xgsg.cfg            |   0
 tests/fixtures/export/SH#601003.csv               |   0
 tests/fixtures/export/SH#601003.txt               |   0
 tests/fixtures/export/SH#601005.txt               |   0
 tests/fixtures/export/SH#601006.txt               |   0
 tests/fixtures/export/SH#601007.txt               |   0
 tests/fixtures/export/SH#601008.txt               |   0
 tests/fixtures/export/SH#601009.txt               |   0
 tests/fixtures/incon.dat                          |   0
 tests/fixtures/vipdoc/ds/lday/4#CF7D0LAO.day      | Bin
 tests/fixtures/vipdoc/ds/lday/4#CF7D0LLS.day      | Bin
 tests/fixtures/vipdoc/sh/fzline/sh688001.lc5      | Bin
 tests/fixtures/vipdoc/sh/lday/sh000001.day        | Bin
 tests/fixtures/vipdoc/sh/lday/sh127021.day        | Bin
 tests/fixtures/vipdoc/sh/lday/sh688001.day        | Bin
 tests/fixtures/vipdoc/sh/lday/sh881478.day        | Bin
 tests/fixtures/vipdoc/sh/minline/sh688001.lc1     | Bin
 tests/fixtures/vipdoc/sz/lday/sz000001.day        | Bin
 tests/fixtures/vipdoc/sz/lday/sz127021.day        | Bin
 tests/quotes/__init__.py                          |   0
 tests/quotes/test_quotes_base.py                  |   0
 tests/quotes/test_quotes_ext.py                   |   0
 tests/quotes/test_quotes_std.py                   |   0
 tests/reader/__init__.py                          |   0
 tests/reader/test_reader_base.py                  |   0
 tests/reader/test_reader_block.py                 |   0
 tests/reader/test_reader_blocknew.py              |   0
 tests/reader/test_reader_ext.py                   |   0
 tests/reader/test_reader_parse.py                 |   0
 tests/reader/test_reader_std.py                   |   0
 tests/requirements.txt                            |   0
 tests/test_adjust.py                              |   0
 tests/test_adjust2.py                             |   0
 tests/test_affair_unit.py                         |   0
 tests/test_affairs.py                             |   0
 tests/test_bestip.py                              |   0
 tests/test_config.py                              |   0
 tests/test_config_setup.py                        |   0
 tests/test_exceptions.py                          |   0
 tests/test_factor.py                              |   0
 tests/test_frequency.py                           |   0
 tests/test_quotes_more.py                         |   0
 tests/test_quotes_unit.py                         |   0
 tests/test_reconnect.py                           |   0
 tests/test_server_more.py                         |   0
 tests/test_server_unit.py                         |   0
 tests/test_tdxfinder.py                           |   0
 tests/test_useless.py                             |   0
 tests/test_xdxr.py                                |   0
 tests/tools/__init__.py                           |   0
 tests/tools/test_customize.py                     |   0
 tests/tools/test_reversion.py                     |   0
 tests/tools/test_tdx2csv.py                       |   0
 tests/utils/__init__.py                           |   0
 tests/utils/test_holiday.py                       |   0
 tests/utils/test_timer.py                         |   0
 tests/utils/test_utils.py                         |   0
 172 files changed, 487 insertions(+), 379 deletions(-)
```

## 最近提交
```
04d3489 按规范整理项目目录结构
f60089e 更新 API 文档：新增复权K线、数据校验、变更日志
cb4c56a 升级版本号至 0.14.0 — 增强功能并下沉通用能力
d32d369 增强功能并下沉通用能力到 opentdx
300248a 消除服务器列表和常量冗余 — 统一从 opentdx 导入
```
