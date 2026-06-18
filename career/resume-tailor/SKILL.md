---
name: resume-tailor
description: "Use when customizing your resume for a specific job — takes the match analysis and generates a tailored version emphasizing matching skills."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [job-hunt, resume, tailoring, career]
    related_skills: [jd-resume-matcher, cover-letter-writer, job-hunt-pipeline]
---

# Resume Tailor

> Tailor your resume for a specific job. Based on JD-Resume matching results, generates a customized version that emphasizes matching skills and fills gaps.

---

## When to Use

- *"Tailor my resume for this software engineer position"*
- *"Customize my resume to highlight the skills this JD asks for"*
- *"帮我根据这个 JD 优化简历"*

---

## Workflow

1. Run `jd-resume-matcher` first to identify gaps
2. For each **missing skill**, the AI adds relevant experience bullet points
3. For each **matched skill**, the AI rewrites descriptions to be more prominent
4. Saves a tailored version

## Output Example

```
# 🎯 简历定制报告

目标岗位匹配度: 31.9%

## 需要补充的技能
- graphql — 在项目经历中补充："
  使用 Apollo Client 和 GraphQL 实现了高效的数据查询"
- kubernetes — 补充："
  使用 Docker + Kubernetes 部署微服务，管理 10+ 节点集群"
- node.js — 补充："
  使用 Node.js + Express 构建 RESTful API"

## 建议强化描述
- docker — 在简历中更突出 Docker 相关的工作成果
- python — 在简历中更突出 Python 相关的工作成果
- react — 在简历中更突出 React 相关的工作成果
```

---

## Usage

```bash
cd ~/dev/job-hunt-tool
source .venv/bin/activate

python3 -m src tailor resume.txt jd.txt --output resume-tailored.md
```
