---
name: api-contract-tester
description: "Use when you need to validate an HTTP API contract against an OpenAPI specification or documented expectations. Generates deterministic smoke tests, checks status/schema/headers, detects breaking response changes, and produces CI-friendly reports without exposing credentials."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [api, openapi, contract-testing, testing, ci, http]
    related_skills: [api-doc-generator, code-review-helper, debugging]
---

# API Contract Tester / API 契约测试器

## Overview — 概述

对 HTTP API 做可重复的契约验证：从 OpenAPI 文档或明确的 endpoint 清单生成安全的 smoke tests，检查状态码、响应头、JSON 字段类型、必填字段和错误响应；将结果输出为人类可读报告与机器可读 JSON，适合本地调试和 CI。默认只访问明确允许的目标，不读取或打印 `.env`、`auth.json` 等凭证。

| 能力 | 输出 | 适用场景 |
|---|---|---|
| 规范解析 | endpoint/method 清单 | OpenAPI 3.x 快速盘点 |
| 合约验证 | status、headers、JSON schema 结果 | 回归测试、发布前检查 |
| 变更检测 | breaking/non-breaking 分类 | API 版本升级 |
| 安全执行 | allowlist、超时、脱敏日志 | CI、第三方 API 集成 |

## When to Use — 适用条件

- “帮我测试这个 OpenAPI 是否和服务实现一致”
- “发布前对 API 做 smoke test”
- “比较 v1 和 v2 的响应契约，找 breaking change”
- “把 API 契约检查接入 CI”

不要用于未获授权的第三方扫描、压力测试、模糊测试或绕过认证。

## Core Workflow — 核心流程

### Step 1: 建立测试边界

确认规范文件、base URL、允许的 HTTP 方法和测试数据。优先使用本地 fixture 或 staging；禁止把真实 token 写入命令行、报告或仓库。

```bash
python3 - <<'PY'
from pathlib import Path
import yaml
p = Path("openapi.yaml")
doc = yaml.safe_load(p.read_text())
assert str(doc.get("openapi", "")).startswith("3."), "仅支持 OpenAPI 3.x"
print(f"paths={len(doc.get('paths', {}))}")
PY
```

若环境没有 PyYAML，使用项目已有依赖；不要为了测试修改生产依赖。

### Step 2: 执行最小安全探针

对每个选定 endpoint：设置连接/总超时、限制响应体大小、记录 URL（去除 query secrets）、状态码和校验摘要。先运行无副作用的 `GET`/`HEAD`；`POST`/`PUT`/`DELETE` 只在用户明确提供 fixture 时执行。

```python
import json, os, urllib.request

url = os.environ["API_BASE_URL"].rstrip("/") + "/health"
req = urllib.request.Request(url, headers={"Accept": "application/json"})
with urllib.request.urlopen(req, timeout=10) as r:
    body = r.read(1_000_000)
    result = {"status": r.status, "content_type": r.headers.get("content-type"),
              "body_bytes": len(body)}
print(json.dumps(result, ensure_ascii=False))
```

认证通过进程环境注入，例如 `API_TOKEN`；报告中只显示 `***`。

### Step 3: 对照契约并生成报告

逐项验证：

1. 实际状态码是否属于 operation 的 `responses`。
2. `Content-Type` 是否匹配声明的 media type。
3. JSON body 的 required 字段是否存在、类型是否正确。
4. 额外字段按项目策略标记为 warning 或 breaking。
5. 将每项结果写入 `api-contract-report.json`，并生成摘要：`PASS/WARN/FAIL`、失败 endpoint、建议修复。

建议退出码：`0=通过或仅 warning`，`1=契约失败`，`2=配置/网络错误`。网络错误不能伪装成契约通过。

### Step 4: 比较版本（可选）

对 OpenAPI 文档做静态 diff：删除 endpoint、删除 required 字段、收窄 enum、把字段类型改窄、移除响应状态码均视为潜在 breaking；新增可选字段通常为 non-breaking。静态 diff 不能替代真实请求验证，必须在报告中区分两者。

## Example Invocations — 示例

### 示例 1：本地 smoke test

**用户：** “用 `openapi.yaml` 测试 `http://localhost:8000`，只跑 GET。”

**Agent：** “已限制到 localhost 和 GET，设置 10 秒超时；读取规范后执行探针，输出 `api-contract-report.json`，失败项按 endpoint/status/schema 分类，不打印认证信息。”

### 示例 2：CI 阻断

**用户：** “把 staging API 的契约失败设为 CI 阻断。”

**Agent：** “使用 `API_BASE_URL` 与 `API_TOKEN` 环境变量，生成 JSON 报告；仅 `FAIL` 返回退出码 1，网络/配置错误返回 2，并将报告作为 CI artifact。”

### 示例 3：版本升级审查

**用户：** “比较 `openapi-v1.yaml` 和 `openapi-v2.yaml`，告诉我有哪些 breaking changes。”

**Agent：** “先做静态 schema diff，再用 staging smoke test 复核关键操作；报告区分删除字段、required 变化、类型收窄和新增可选字段。”

## Common Pitfalls — 常见陷阱

| 问题 | 解决方案 |
|---|---|
| 把网络超时当成 API 通过 | 使用独立错误码 2，并报告根因 |
| 在 URL 或日志中泄露 token | 只从环境变量读取，统一脱敏 |
| 对生产写接口做自动测试 | 默认 GET/HEAD；写操作必须有明确 fixture 和授权 |
| 只检查 200，不检查声明响应 | 按 OpenAPI `responses` 校验所有允许状态码 |
| JSON Schema `$ref` 未展开 | 解析本地/允许的 remote refs，并记录解析来源 |
| 额外字段一律判 breaking | 遵循项目兼容策略；将 warning 与 fail 分开 |
| 大响应拖垮 CI | 限制读取字节数、超时和并发数 |

## Verification Checklist — 验证清单

- [ ] 只访问用户授权的 base URL，且 endpoint 在 allowlist 内
- [ ] OpenAPI 版本和 paths 已解析
- [ ] GET/HEAD 探针在超时与响应大小限制下执行
- [ ] 状态码、Content-Type、required 字段和类型已验证
- [ ] token、cookie、query secret 未进入日志或报告
- [ ] 网络错误与契约失败使用不同退出码
- [ ] JSON 报告可被 CI 解析
- [ ] 至少覆盖一个通过样例和一个失败样例
- [ ] 写操作未被默认执行

## Data Sources & Accuracy — 数据来源与准确性

- 契约来源：用户提供的 OpenAPI 3.x 文件或明确的接口文档。
- 运行时来源：指定 base URL 的真实 HTTP 响应；结果只代表测试时刻和测试数据。
- 静态 breaking-change 判定：基于常见 OpenAPI 兼容性规则，复杂业务约束仍需人工审查。
- 认证、限流、地域路由和动态字段可能导致偶发差异；报告必须记录时间、环境和测试配置。
