# {{TITLE}}

> **Slug:** `{{SLUG}}` · **Created:** {{DATE}} · **Status:** active · **Tags:** {{TAGS}}

---

## 🎯 Goal

> 一句话写出这个项目要产出的**可验证产物**。模糊即是失败信号。
>
> 例：*"发布 Launch Deck v3 并在 Q3 评审会上拿到预算签字。"*

{{GOAL}}

---

## 📐 Scope

**In (要做):**
- {{IN_1}}

**Out (不做):**
- {{OUT_1}}

**Non-goals (明确不解决):**
- {{NONGOAL_1}}

---

## 🎯 Current Focus

> **当前在做：** {{FOCUS_WHAT}}
>
> **下一动作：** {{FOCUS_NEXT}}

*最后更新：{{FOCUS_UPDATED}}*

---

## 🔁 Open Loops

> 打开但未关闭的线程。格式：`- [ ] [id#NN] <描述> — opened YYYY-MM-DD`

- [ ] [id#01] {{LOOP_1}} — opened {{DATE}}

---

## 🧾 Decisions

> 决策是**只追加**日志。每条必须链接到 `decision-journal`。

- {{DATE}} — {{DECISION_1}} → `decision-journal/{{DECISION_SLUG}}.md`

---

## 🚧 Blockers

> 按"卡在谁身上"分类。是 *你*？*对方*？*等待*？还是*不清楚*？

### You
- _(还没有)_

### Them
- _(还没有)_

### Waiting
- _(还没有)_

### Unclear
- _(还没有)_

---

## 🅿️ Parking Lot

> 想法、片段、半成品——现在不可执行，但扔掉可惜。
> 格式：`- [YYYY-MM-DD HH:MM] <text>`

- [{{DATE}} 09:00] _(第一次记录时删除这一行)_

---

## 📓 Log

> 时间戳日记。每天一个二级标题，自由条目。

## {{DATE}}
- _(_canvas 创建)_
- ↩ switched to `{{SLUG}}`

---

<!--
  本文件由 deep-work-canvas skill 维护。
  结构为 8 个固定 section，顺序不可变：
  Goal · Scope · Current Focus · Open Loops · Decisions · Blockers · Parking Lot · Log

  验证：python3 scripts/validate.py <this-file>.md
-->
