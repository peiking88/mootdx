#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

failures=0

ok() {
    printf '[OK] %s\n' "$1"
}

warn() {
    printf '[WARN] %s\n' "$1"
}

fail() {
    printf '[FAIL] %s\n' "$1"
    failures=$((failures + 1))
}

check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        ok "命令可用: $1"
    else
        fail "命令缺失: $1"
    fi
}

echo "== 项目环境完整性检查 =="

for dir in docs cfg src scripts tests output; do
    if [[ -d "$dir" ]]; then
        ok "目录存在: $dir"
    else
        fail "目录缺失: $dir"
    fi
done

check_command git
check_command cmake
check_command ninja
check_command nproc

if [[ "$(git config --get user.name || true)" == "peiking88" ]]; then
    ok "Git user.name 正确"
else
    fail "Git user.name 不是 peiking88"
fi

if [[ "$(git config --get user.email || true)" == "peiking88@users.noreply.github.com" ]]; then
    ok "Git user.email 正确"
else
    fail "Git user.email 不正确"
fi

origin_url="$(git remote get-url origin 2>/dev/null || true)"
if [[ "$origin_url" == "https://github.com/peiking88/mootdx.git" ]]; then
    ok "origin 地址正确"
else
    fail "origin 地址不正确: ${origin_url:-未设置}"
fi

if [[ -n "${GIT_USERNAME:-}" && -n "${GIT_PASSWORD:-}" ]]; then
    ok "Git 环境变量已设置: GIT_USERNAME/GIT_PASSWORD"
else
    warn "Git 环境变量未完整设置: GIT_USERNAME/GIT_PASSWORD"
fi

if git grep -n "bgithub\\.xyz" -- . ':!external/**' >/tmp/project_bgithub_hits.$$ 2>/dev/null; then
    cat /tmp/project_bgithub_hits.$$
    rm -f /tmp/project_bgithub_hits.$$
    fail "发现旧 GitHub 镜像域名引用"
else
    rm -f /tmp/project_bgithub_hits.$$
    ok "未发现旧 GitHub 镜像域名引用"
fi

if git grep -n "http\\.sslVerify=false" -- . ':!external/**' >/tmp/project_ssl_hits.$$ 2>/dev/null; then
    cat /tmp/project_ssl_hits.$$
    rm -f /tmp/project_ssl_hits.$$
    fail "发现禁止的 SSL 校验配置"
else
    rm -f /tmp/project_ssl_hits.$$
    ok "未发现禁止的 SSL 校验配置"
fi

if git diff --cached --name-only | grep -E '^external/' >/tmp/project_external_staged.$$ 2>/dev/null; then
    cat /tmp/project_external_staged.$$
    rm -f /tmp/project_external_staged.$$
    fail "暂存区包含 external/ 内容"
else
    rm -f /tmp/project_external_staged.$$
    ok "暂存区未包含 external/ 内容"
fi

if [[ -n "${VIRTUAL_ENV:-}" ]]; then
    ok "虚拟环境已激活: $VIRTUAL_ENV"
else
    warn "当前未激活虚拟环境；运行测试前必须先激活"
fi

if [[ "$failures" -eq 0 ]]; then
    echo "== 检查完成: 通过 =="
else
    echo "== 检查完成: 失败 ${failures} 项 =="
    exit 1
fi
