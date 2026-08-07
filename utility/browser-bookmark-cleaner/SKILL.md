---
name: browser-bookmark-cleaner
description: "Use when cleaning, deduplicating, classifying, or auditing browser bookmarks. Exports bookmarks safely, normalizes URLs, detects duplicates and dead links, assigns searchable tags, and produces a reviewable local report without deleting anything by default."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [utility, bookmarks, browser, cleanup, deduplication, url, privacy, local-first]
    related_skills: [web-clipper, file-organizer, website-health-monitor, format-converter]
---

# Browser Bookmark Cleaner / 浏览器书签清理器

> 把多年积累的书签从“数字考古遗址”变成可搜索、可维护的知识入口；先备份、再分析、最后由人确认删除。

## Overview / 概述

Browser Bookmark Cleaner 面向 Chrome、Chromium、Firefox、Safari 等浏览器导出的 HTML 书签。它在本地完成解析、URL 规范化、重复检测、链接健康检查、标签建议和审阅报告生成。默认只读分析，不修改浏览器数据库，也不自动删除任何条目。

| 能力 | 输出 | 默认安全策略 |
|---|---|---|
| 导入与备份 | 原始 HTML 副本、解析清单 | 原文件只读 |
| URL 规范化 | 去除追踪参数、统一尾斜杠和主机大小写 | 保留原始 URL |
| 重复检测 | 精确重复、规范化重复、疑似同页 | 只生成候选，不删除 |
| 链接健康检查 | HTTP 状态、最终 URL、耗时、错误类型 | 限速、尊重 robots/站点政策 |
| 自动分类 | 基于域名、标题、路径的标签建议 | 建议需人工确认 |
| 审阅报告 | Markdown/CSV/JSON | 可回滚、可追溯 |

推荐工作目录：`~/Documents/bookmark-cleaner/`。将浏览器导出的文件放在该目录，避免把浏览器私有数据库复制到不受控位置。

## When to Use / 适用场景

- “我的浏览器书签太乱了，找出重复和失效链接。”
- “把 Chrome 书签按工作、学习、购物、阅读分类。”
- “清理所有 UTM、fbclid 等追踪参数，但保留原始链接。”
- “比较两个浏览器导出的书签，找出新增和消失的条目。”
- “生成一个我可以逐项确认的删除候选清单。”

不用于：直接修改浏览器内部数据库；绕过登录、验证码或访问控制；批量抓取需要认证的站点；未经用户确认永久删除书签。

## Core Workflow / 核心工作流

### Step 1：导出并建立安全快照

先在浏览器中使用“导出书签”功能，得到 `bookmarks.html`。不要读取 `~/Library/Application Support/Google/Chrome/.../Bookmarks` 等正在被浏览器写入的数据库。

```bash
set -euo pipefail
mkdir -p ~/Documents/bookmark-cleaner/{input,backup,output}
cp ~/Downloads/bookmarks.html \
  ~/Documents/bookmark-cleaner/backup/bookmarks-$(date +%Y%m%d-%H%M%S).html
cp ~/Downloads/bookmarks.html \
  ~/Documents/bookmark-cleaner/input/bookmarks.html
shasum -a 256 ~/Documents/bookmark-cleaner/input/bookmarks.html
```

记录来源浏览器、导出时间和文件哈希。任何后续报告都引用该快照，不覆盖原文件。

### Step 2：解析、规范化和去重

使用 Python 标准库解析 Netscape Bookmark HTML；不要把标题或 URL 拼进 shell 命令。下面的最小脚本可提取书签并生成规范化字段：

```python
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import json, re, sys

TRACKING = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
            "gclid", "fbclid", "mc_cid", "mc_eid", "ref", "ref_"}

def normalize_url(raw):
    p = urlsplit(raw.strip())
    if p.scheme.lower() not in {"http", "https"} or not p.netloc:
        return raw.strip()
    host = p.hostname.lower() if p.hostname else ""
    if p.port and not ((p.scheme.lower() == "http" and p.port == 80) or
                       (p.scheme.lower() == "https" and p.port == 443)):
        host += f":{p.port}"
    query = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
             if k.lower() not in TRACKING and not k.lower().startswith("utm_")]
    path = re.sub(r"/{2,}", "/", p.path or "/")
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit((p.scheme.lower(), host, path, urlencode(query), ""))

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.items=[]; self.current=None; self.folder=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag == "h3": self.current={"title":"", "folder": "/".join(self.folder)}
        elif tag == "a" and a.get("href"):
            self.current={"title":"", "url":a["href"], "folder":"/".join(self.folder)}
    def handle_data(self, data):
        if self.current is not None: self.current["title"] += data.strip()
    def handle_endtag(self, tag):
        if tag == "a" and self.current and "url" in self.current:
            x=self.current; x["normalized_url"]=normalize_url(x["url"]); self.items.append(x); self.current=None
        elif tag == "h3" and self.current:
            self.folder.append(self.current["title"]); self.current=None

p=Parser(); p.feed(Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace"))
for i, x in enumerate(p.items, 1): x["id"]=i
Path(sys.argv[2]).write_text(json.dumps(p.items, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"parsed={len(p.items)} output={sys.argv[2]}")
```

运行：

```bash
python3 parse_bookmarks.py input/bookmarks.html output/bookmarks.json
```

去重分三层：

1. `url` 完全相同：确定重复。
2. `normalized_url` 相同：追踪参数或尾斜杠造成的重复，优先保留标题更完整、文件夹更明确的条目。
3. 同域名、同路径但查询参数不同：只标记 `review_candidate`，不得自动合并。

每个候选必须保留 `keep_id`、`duplicate_ids`、判定规则和原始 URL，确保用户能恢复。

### Step 3：健康检查、分类与人工审阅

对公开 HTTP(S) URL 做有限速探测。先 `HEAD`，遇到 `405` 或无结果再用小型 `GET`；设置超时、并发上限和 User-Agent，不重试无限次：

```python
import requests, time

def check(url, timeout=10):
    try:
        r=requests.head(url, allow_redirects=True, timeout=timeout,
                        headers={"User-Agent":"Hermes-Bookmark-Audit/1.0"})
        if r.status_code in {405, 403}:
            r=requests.get(url, allow_redirects=True, timeout=timeout,
                           headers={"User-Agent":"Hermes-Bookmark-Audit/1.0"},
                           stream=True)
        return {"status":r.status_code, "final_url":r.url,
                "ok":200 <= r.status_code < 400}
    except requests.RequestException as e:
        return {"status":None, "ok":False, "error":type(e).__name__}

for item in items:
    item["health"]=check(item["normalized_url"])
    time.sleep(0.25)
```

状态解释：`2xx` 通常可用；`3xx` 记录最终 URL；`401/403` 是受限，不等于失效；`404/410` 是强失效候选；超时、DNS、TLS 错误应单独标注。对 `file:`, `javascript:`, 内网地址和需要认证的域名默认跳过网络检查。

分类建议只作为建议：

- 优先使用原文件夹；
- 再依据域名/路径词典生成 `work`、`learning`、`dev`、`finance`、`shopping`、`reading`、`news` 等标签；
- 标出冲突，例如文件夹为“工作”但内容像购物；
- 不把 URL 中的邮箱、token、查询参数复制进公开报告。

生成 `output/review.md`，按以下顺序排列：失效候选、规范化重复、长期未访问/无日期条目、分类冲突、其余统计。每行包含 ID、标题、文件夹、域名、状态、建议动作和依据。用户确认后，才生成清理后的 HTML；永远保留原始快照。

## Example Invocations / 示例调用

### 示例 1：找重复和失效

**User：**“清理我的 Chrome 书签，找出重复和死链，但不要删除。”

**Agent：**“请使用浏览器导出 `bookmarks.html` 并提供路径。我会创建带哈希的只读快照，解析后输出重复组、HTTP 状态和可审阅 Markdown；`403/401` 会标记为受限，不会误判为死链，也不会删除原书签。”

### 示例 2：去追踪参数

**User：**“去掉书签里的 UTM 参数，保留原始链接。”

**Agent：**“将生成 `original_url` 与 `normalized_url` 两列，并先报告会发生的变化。只有你确认后才导出新 HTML；登录回调、短链参数和疑似业务参数不会自动删除。”

### 示例 3：两个浏览器合并

**User：**“把 Safari 和 Firefox 书签合并，重复的优先保留 Safari 文件夹结构。”

**Agent：**“我会分别记录来源，按规范化 URL 建立重复组；Safari 仅作为默认保留项，冲突标题和不同查询参数仍进入人工审阅。输出合并预览和回滚所需的原始快照。”

## Common Pitfalls / 常见陷阱

| 问题 | 解决方案 |
|---|---|
| 直接修改浏览器内部 Bookmarks 数据库 | 只处理导出的 HTML，关闭浏览器后由用户导入结果 |
| 把 403/401 当成死链 | 标记为 `restricted`，不自动删除 |
| 删除所有查询参数 | 只删除已知追踪参数；业务参数保留并进入审阅 |
| 只按 URL 去重导致不同文章被合并 | 仅完全/规范化相同才判定重复；同路径不同 query 只候选 |
| 大量并发探测触发封禁 | 低并发、固定间隔、超时上限、失败不无限重试 |
| 生成报告泄露私有 URL | 脱敏 token、session、邮箱和内网主机；报告默认本地 |
| 忽略浏览器文件夹结构 | 原样保存 `folder`，优先保留用户上下文 |
| 清理后无法恢复 | 原始 HTML、哈希、清理前后 diff 必须永久保留一份 |
| 把“没有日期”解释成“很久没用” | 只说明元数据缺失，不推断访问频率 |

## Verification Checklist / 验证清单

- [ ] 输入是浏览器导出的 HTML，不是正在使用的私有数据库
- [ ] 原始文件已复制到 `backup/` 并记录 SHA-256
- [ ] 解析数量与原文件中的书签数量大致一致，异常已报告
- [ ] 每条记录保留原始 URL、规范化 URL、标题和文件夹
- [ ] 重复组包含可回滚的 ID 映射
- [ ] 网络检查设置超时、限速，且未访问认证资源
- [ ] 401/403、超时、DNS/TLS 错误未被统称为 404
- [ ] 追踪参数规则可审计，未知参数未静默删除
- [ ] 报告未包含 API key、cookie、session、邮箱或私有内网地址
- [ ] 未经用户确认没有删除或覆盖任何书签
- [ ] 清理后的 HTML 可被浏览器重新导入
- [ ] 清理前后数量、重复数、失效候选数均在报告中明确

## Data Sources & Accuracy / 数据来源与准确性

- **首要数据源**：用户导出的 Netscape Bookmark HTML；它只代表导出时刻的书签状态。
- **健康状态来源**：目标 URL 的 HTTP 响应、最终重定向 URL 和本地 DNS/TLS 结果。网络状态是时间点快照，不保证页面长期可用。
- **访问限制**：不绕过登录、验证码、robots 或站点访问控制；受限结果必须标记为未知/受限。
- **规范化准确性**：追踪参数名单是启发式规则；业务 query 参数可能影响内容，任何有风险的变化必须人工确认。
- **分类准确性**：标签来自文件夹、域名和标题启发式推断，不是事实分类；冲突必须显式展示。
- **隐私**：全流程默认本地执行。`.env`、`auth.json`、cookie、Bearer token、个人 URL 和浏览历史不应进入 Git 或公开报告。
