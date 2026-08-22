---
name: prompt-refiner
description: "Turn vague or underperforming prompts into well-structured, effective ones — diagnose failure modes, apply the R-T-C-E framework (Role/Task/Context/Example), and iterate to a prompt that reliably produces the output you want."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [prompt-engineering, prompt-refining, llm, optimization, writing]
    related_skills: [prompt-library, prompt-benchmarker, llm-output-validator, model-comparator]
---

# Prompt Refiner（Prompt 精炼器 / 提示词优化）

> 把"说不清要什么"的 prompt，重写成"模型一次就懂"的 prompt。本 skill 诊断一条 prompt 为什么不好，用 R-T-C-E 框架重构它，注入示例与输出格式约束，并给出可执行的验证方法。**它不管理 prompt（那是 prompt-library 的活），也不做 A/B 实验（那是 prompt-benchmarker 的活）——它只负责把烂 prompt 变成好 prompt。**

| Capability | Description |
|-----------|-------------|
| 🔍 失败模式诊断 | 识别 6 类常见 prompt 通病：目标模糊 / 缺上下文 / 无输出格式 / 无约束 / 无人设 / 无示例 |
| 🧱 R-T-C-E 重构 | Role（角色）→ Task（任务）→ Context（上下文）→ Example（示例）四段式模板 |
| 📐 输出格式强制 | 把"随便写"变成"给 JSON / Markdown 表格 / 固定长度"的确定性输出 |
| 🚫 约束注入 | 长度、语气、语言、禁止项、边界条件显式声明 |
| ✨ Few-shot 示例 | 用 1-2 个高质量示例教会模型"你要的到底是什么" |
| 🔁 迭代验证 | 重构 → 试跑 → 对照失败模式 → 再改的闭环 |
| 🌐 双语支持 | 中文 / English prompt 同样适用；输出可要求中英对照 |

---

## When to Use

- *"帮我改一下这个 prompt，它总是不符合我的要求"*
- *"我的 prompt 写得太烂了，帮我结构化一下"*
- *"让 AI 给我写周报，但每次格式都不一样，怎么办？"*
- *"这个 prompt 输出太长了/太短了/太啰嗦了，帮我约束一下"*
- *"我的 prompt 缺了什么？为什么它不理解我的真实需求？"*
- *"Refine this prompt: 'write me something about AI'"*
- *"把这段自然语言需求转换成一条专业 prompt"*
- *"This prompt works 50% of the time — fix it"*

---

## Core Workflow

### Step 1: 诊断 —— 找出 prompt 的失败模式

拿到任意 prompt 后，对照下表逐项打勾。**先诊断，再动手改。** 多数烂 prompt 同时命中 2-4 项。

```markdown
| # | 失败模式 | 判断问题 | 典型症状 |
|---|---------|---------|---------|
| 1 | 🎯 目标模糊 | "要什么"说不清？ | 输出泛泛而谈，没有可行动的结论 |
| 2 | 🧠 缺上下文 | 背景信息缺失？ | 模型瞎猜场景、假设错误前提 |
| 3 | 📐 无输出格式 | 没规定格式？ | 每次结构都不同，无法直接复用 |
| 4 | 🚫 无约束 | 长度/风格/语言没限定？ | 输出过长、太正式/太随意、中英混杂 |
| 5 | 🎭 无人设 | 没指定角色视角？ | 语气平庸，缺乏专业深度 |
| 6 | ✨ 无示例 | 没给"长什么样"的参考？ | 格式对但内容不是你要的方向 |
```

**输出诊断结果：**
```markdown
诊断：该 prompt 命中 4 项失败模式 —— #1 目标模糊、#2 缺上下文、#3 无输出格式、#6 无示例。
严重度：高。建议按 Step 2 完整重构。
```

### Step 2: 重构 —— 套用 R-T-C-E 四段式模板

将原 prompt 的内容拆解后填入以下模板（**不是所有字段都要有，但 T 必须有**）：

```markdown
## Role（角色）—— 模型以什么身份回答
你是一位资深 {专业领域} 专家，擅长 {相关能力}。

## Task（任务）—— 明确动词 + 交付物（必填）
请 {分析/撰写/总结/对比/生成} {对象}，目标是 {具体目的}。

## Context（上下文）—— 背景、受众、已知条件
- 背景：{情况说明}
- 受众：{谁看这份输出}
- 已知：{材料/数据/约束条件}

## Example（示例）—— 让模型对齐"什么算好"
示例 1：
  输入：{示例输入}
  期望输出：{示例输出}
```

### Step 3: 注入输出格式与硬约束

在 R-T-C-E 之后追加"输出格式"与"约束"小节（失败模式 #3/#4 的对应解药）：

```markdown
## 输出格式（强制）
- 结构：{Markdown 表格 / JSON / 三段式 / 分点列表}
- 长度：{≤300 字 / 5 个要点 / 每点 ≤50 字}
- 语言：{中文 / English / 中英对照}
- JSON 时必须给出 schema 示例

## 约束（硬性）
- 禁止：{不要提建议 / 不要编造数据 / 不要用营销话术}
- 边界：{只基于给定材料 / 不知道就明说 / 保留不确定性}
- 风格：{直接 / 口语 / 正式 / 毒舌幽默}
```

### Step 4: 迭代验证（闭环）

1. **试跑**：用重构后的 prompt 实际调用一次模型，拿真实输出
2. **对照**：输出是否满足全部约束？哪一项没做到？
3. **定位**：没做到 → 回 Step 1 判断是缺格式还是缺示例；缺示例就补 Example，缺约束就补硬性限制
4. **固化**：把最终版本存入 `~/.hermes/data/prompts.json`（交给 prompt-library skill 管理），或直接交付给用户

> 一次就写对是例外，不是常态。预期 2-3 轮迭代。每次只改一处，否则无法判断是哪处改动起效。

---

## Example Invocations

### 例 1：从"一句话"到"专业 prompt"

**用户说：** *"写个 prompt，让 AI 帮我分析竞品。"*

**Agent 诊断：** 命中 #1 目标模糊、#2 缺上下文、#3 无输出格式、#5 无人设。

**Agent 交付（重构后）：**
```markdown
你是一位 SaaS 产品分析师，擅长竞争情报分析。

请对 {竞品名} 进行竞争分析，目标是判断它对我方产品 {产品名} 的威胁等级。

背景：我方是 {定位}，目标市场 {市场}；以下是竞品公开信息：{粘贴材料}
受众：产品负责人，需在 10 分钟内读完并做决策。

## 输出格式
| 维度 | 分析 | 对我方威胁(1-5) |
|------|------|----------------|
| 产品功能 | ... | ... |
| 定价策略 | ... | ... |
| 市场动作 | ... | ... |
| 增长迹象 | ... | ... |
最后给出一句话结论 + 我方应采取的 1 个优先行动。

## 约束
- 只基于给定材料，不要编造数据
- 不确定的信息标注"未知"
- 全文 ≤500 字，中文
```

### 例 2：修复"格式不稳定"问题

**用户说：** *"让 AI 写周报，但每次格式都不一样，帮我固定下来。"*

**Agent 诊断：** 命中 #3 无输出格式、#6 无示例（这是最典型的"格式漂移"根因）。

**Agent 交付（重构后）：**
```markdown
你是一位严谨的职场周报助手。请根据我的工作记录生成周报。

工作记录：{粘贴本周记录}
受众：直属上级，偏好量化结果。

## 输出格式（必须严格遵守，不要增删小节）
### 本周完成
- 每条以动词开头，格式：【事项】→【量化结果】
### 下周计划
- 3-5 条，按优先级排序
### 风险与求助
- 无则写"无"

## 示例
输入："周二修了登录 bug；周三上线了新版本；周四用户反馈加载变快"
期望输出：
### 本周完成
- 【修复登录 bug】→ 影响用户约 2000 人，问题 24h 内解决
- 【上线 v2.3】→ 全量发布，无回滚
- 【优化加载速度】→ 首屏时间 3.2s → 1.8s（用户正向反馈）
（示例为格式示范，量化数字需以实际记录为准）
```

### 例 3：英文 prompt 精炼

**用户说：** *"Refine this prompt: 'write me something about AI'"*

**Agent 诊断：** Vague goal (#1), no output format (#3), no constraints (#4), no persona (#5).

**Agent 交付（重构后）：**
```markdown
You are a technology writer specializing in AI for business audiences.

Write a 400-word explainer about the difference between generative AI and predictive AI,
aimed at a non-technical product manager who needs to make a buy-vs-build decision.

Structure:
1. One-line plain-English definition of each
2. A side-by-side comparison table (capability, best use, typical cost, risk)
3. A concrete recommendation framework (3 questions to ask before choosing)

Constraints:
- No jargon without a one-line explanation
- No speculation about future capabilities
- End with 3 actionable questions the PM can take to their team
```

---

## Common Pitfalls

| 问题 | 解决方案 |
|------|---------|
| 改完的 prompt 比原来还长，用户看不懂 | R-T-C-E 不是越长越好；能一句话说清任务就别堆砌人设。超过 150 字而无信息量 = 失败 |
| 只加了"请认真回答"这类废话 | 无效约束。改为可验证的硬约束："输出 ≤300 字"、"只基于材料" |
| 输出格式指定了，但模型仍不遵守 | 追加 few-shot 示例（Step 4），示例比描述更能约束格式 |
| 一次改太多变量，无法定位哪个改动有效 | 单轮迭代只改一处；对照失败模式逐条修复 |
| 用户没给上下文就要求重构 | 先问 3 个最小问题：目标受众？输出给谁用？有没有参考材料？没有就生成带 `{占位符}` 的模板 |
| 示例被模型逐字照抄（含编造数字） | 在示例后声明"示例仅示范格式，内容需基于真实数据" |
| 把 prompt 优化当成玄学 | 一切改动都要落到 6 个失败模式之一；改不出就回到 Step 1 重新诊断 |
| 重构后从不试跑 | 不试跑的重构是猜。至少真实调用一次，把输出贴回给用户对比 |

---

## Verification Checklist

- [ ] 已用 6 项失败模式逐条诊断原 prompt，并输出命中项
- [ ] 重构后的 prompt 包含明确的 Task（动词 + 交付物）
- [ ] 有上下文信息或 `{占位符}` 让用户补充
- [ ] 输出格式被显式指定（结构 / 长度 / 语言）
- [ ] 硬约束被显式声明（禁止项 / 边界 / 风格）
- [ ] 需要时提供了 1-2 个 few-shot 示例
- [ ] 已实际试跑一次，输出满足全部约束
- [ ] 迭代过程只改了一处变量（如有迭代）
- [ ] 交付时附上"改了什么 / 为什么改"的简短说明

---

## Data Sources & Accuracy

- **本 skill 不依赖任何外部 API 或数据源**；所有诊断与重构逻辑基于可验证的 prompt 工程最佳实践（如 Anthropic / OpenAI 官方 prompt 工程指南中关于角色、few-shot、输出格式约束的通用原则）。
- **示例输出为格式示范**，其中的数字/事实均为占位，使用时必须替换为用户真实材料，避免模型照抄示例导致编造。
- 重构效果的"准确率"只能通过真实试跑验证——这也是 Step 4 为什么是强制步骤。
- 相关延伸：写好的 prompt 用 `prompt-library` 保存复用；多条候选版本用 `prompt-benchmarker` A/B 对比；最终输出用 `llm-output-validator` 校验质量。
