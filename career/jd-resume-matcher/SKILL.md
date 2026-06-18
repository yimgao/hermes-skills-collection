---
name: jd-resume-matcher
description: "Use when matching your resume against a job description — computes TF-IDF similarity, identifies missing skills, and generates adjustment suggestions."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [job-hunt, resume, jd-matching, nlp, career]
    related_skills: [resume-tailor, cover-letter-writer, job-hunt-pipeline]
---

# JD-Resume Matcher

> Match your resume against any job description. Uses TF-IDF cosine similarity to compute a match score, identifies missing skills, and generates actionable suggestions.

---

## When to Use

- *"Match my resume against this job description"*
- *"What skills am I missing for this role?"*
- *"How well does my resume fit this full-stack position?"*

---

## Output Example

```
📊 匹配分析结果
  匹配度: 31.9% (medium)
  JD 技能数: 6
  简历技能数: 4
  共同技能: 3

🔴 缺失技能 (3)
  • graphql
  • kubernetes
  • node.js

✅ 已匹配技能 (3)
  docker, python, react

💡 调整建议
  🔴 缺失关键技能: graphql, kubernetes, node.js
  📝 匹配度中等，建议强化 JD 中高频技术栈描述
```

---

## Usage

```bash
cd ~/dev/job-hunt-tool
source .venv/bin/activate

# 保存你的简历到文件
echo "你的简历内容..." > resume.txt
echo "JD内容..." > jd.txt

# 运行匹配
python3 -m src match --resume resume.txt --jd jd.txt

# JSON 格式输出（适合程序处理）
python3 -m src match --resume resume.txt --jd jd.txt --json-output
```
