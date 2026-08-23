---
name: message-tone-adjuster
description: "Rewrite any draft message in the right tone — polite, assertive, diplomatic decline, gentle nudge, apology, formal, casual. Chinese/English workplace culture adaptation. Daily-use message fixer."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [communication, tone, rewriting, email, message, culture, chinese-english, workplace, diplomacy, daily-use]
    related_skills: [email-composer, meeting-minutes-generator, presentation-helper]
---

# Message Tone Adjuster — 消息语气改写器

> 把"发出去会后悔"的消息，改写成"对方看了会舒服"的消息。本 skill 接收任何草稿（邮件、微信、Slack、拒绝信、催款单），按目标语气重写，并标注中美职场沟通的文化差异。**它不负责从零起草（那是 email-composer 的活）——它只负责把已有的文字调成对的"味道"。**

| Capability | Description |
|-----------|-------------|
| 🎭 8 种语气库 | 礼貌 Polite / 坚决 Assertive / 委婉拒绝 Diplomatic Decline / 温柔催办 Gentle Nudge / 真诚道歉 Apology / 职场正式 Formal / 轻松亲切 Casual / 自信自荐 Confident Self-Promo |
| 🌐 中美文化适配 | Direct vs Indirect、邮件 vs IM、称谓与落款差异、Hi X vs Dear X 判断 |
| 📧 多渠道输出 | 同一内容同时给出邮件版（subject+正文+落款）与 IM 版（≤200 字微信/Slack） |
| ⚠️ 危险信号扫描 | 检测原稿中的攻击性/被动性/模糊性信号，改写前先指出 |
| 🔄 力度可调 | tone-strength 1-5：从"微调语气"到"彻底重写"，保留原意不变 |
| 🧪 对照表输出 | 原文 vs 改写 vs 改动理由，逐句可审计 |
| 🔒 本地执行 | 不调用任何外部服务，隐私安全 |

---

## When to Use

- *"帮我把这条消息改得礼貌一点，我要拒绝客户的砍价"*
- *"这封邮件太冲了，帮我改成正式版"*
- *"同事欠我三天的回复，怎么催才不尴尬？"*
- *"老板问我要不要接这个活，我想说不——怎么说得体？"*
- *"给美国客户写英文邮件，怎么表达才符合他们的习惯？"*
- *"帮我把这段中文翻译+改写成英文的礼貌版本"*
- *"这句话太软了，帮我写得有底气一点（但要保持专业）"*
- *"Rewrite this email so it sounds less passive-aggressive"*
- *"我想跟供应商讲价，帮我起草一个委婉但坚定的版本"*

---

## Core Workflow

### Step 1: 解析 —— 原文、受众、渠道、目标

拿到任意草稿后，先回答 4 个问题，**不要跳过直接改写**：

```markdown
1. 原意是什么？   → 用一句话概括这条消息真正要传达的核心诉求
2. 受众是谁？     → 老板 / 客户 / 同事 / 下属 / 供应商 / 陌生人？年龄与文化背景？
3. 渠道是什么？   → 邮件 / 微信 / Slack / LinkedIn？邮件更正式，IM 更短
4. 目标效果？     → 让对方答应？不伤感情地拒绝？催而不怒？挽回关系？
```

**同时运行危险信号扫描**，在原稿中标记以下问题（输出时列出）：

| 信号 | 例子 | 风险 |
|------|------|------|
| 😤 攻击性 | "你为什么不回我？" | 引发对抗 |
| 🙈 被动性 | "如果方便的话……不好意思打扰了" | 诉求被忽略 |
| 🌫️ 模糊性 | "尽快" "大概" "再说" | 对方无法行动 |
| 📖 冗长 | 5 行能说完的话写 20 行 | 对方不看 |
| ✂️ 负面开场 | 第一句就是抱怨 | 先入为主 |

### Step 2: 选择语气模式并改写

根据 Step 1 的解析结果选择语气模板。**改写的铁律：保留原意，只换表达。**

| 模式 | 适用场景 | 核心技巧 |
|------|---------|---------|
| 😊 礼貌 Polite | 日常请求、初次联系 | 先谢后求、给对方台阶、结尾留余地 |
| 💪 坚决 Assertive | 讲价、拒绝不合理要求 | 用"我"陈述立场、给出理由+替代方案、不解释过度 |
| 🤝 委婉拒绝 Diplomatic Decline | 不想接的活、降价请求 | 先肯定→说限制→给替代→留后路 |
| ⏰ 温柔催办 Gentle Nudge | 追回复、催款、催文档 | 假定对方"只是忘了"，给 deadline 和"如已完成请忽略" |
| 🙏 真诚道歉 Apology | 犯错、延迟、误发 | 认错具体化→解释但不说"都是因为"→补救措施→时限 |
| 🏢 职场正式 Formal | 上级、外部客户、书面记录 | 完整句式、无 emoji、明确标题、正式落款 |
| 😄 轻松亲切 Casual | 熟人同事、团队群 | 短句、口语化、可带 1 个 emoji、不用敬语 |
| 🚀 自信自荐 Confident Self-Promo | 求加薪、申请项目、自我推荐 | 数据+成果量化、主动要结论、不带歉意的请求 |

**英文沟通文化要点（中美差异）：**
- 中文倾向**间接**（"有个小事想麻烦您"），英文倾向**直接+礼貌壳**（"I wanted to follow up on…" 开头直说诉求）
- 英文邮件常用 **buffer 开头**（"Hope you're doing well"）但只放一句，不放三段寒暄
- 称谓：中文"X总/老师"，英文已知姓名用 `Hi FirstName`，未知用 `Dear Mr./Ms. LastName`，忌用 `Dear Sir/Madam`
- 中文"尽快" → 英文给具体时间（"by EOD Thursday"）
- 中文"不好意思"高频自贬 → 英文慎用 "Sorry"（过度道歉显得不专业），改用 "Thank you for your patience"

### Step 3: 输出对照表 + 自查

输出格式固定为：

```markdown
## 改写结果

### 📋 危险信号（原稿）
- [ ] 😤 攻击性：第 2 句"你为什么不回我"
- [ ] 🌫️ 模糊性："尽快回复"

### 📧 邮件版
**Subject:** …
（正文，含落款）

### 💬 IM 版（≤200 字）
（短版本）

### 🧪 对照表
| 原文 | 改写 | 理由 |
|------|------|------|
| 你为什么不回我 | 想跟进一下上次的进展 | 去攻击性，保留催促意图 |

### ✅ 自查
- 原意保留？ 是/否
- 语气匹配受众？ 是/否
- 渠道适配？ 是/否
```

---

## Example Invocations

### Example 1: 催同事回复（中文 IM）

**用户**: 帮我改一下这条消息："你为什么不回我？我周三就发你了。"
**Agent**:

```
### 📋 危险信号
- 😤 攻击性："你为什么不回我"
- 📖 负面开场：以质问开头

### 💬 IM 版（温柔催办）
"Hi 小王，周三发你的那份数据报告想确认一下收到了没～如果方便的话，今天下班前能给我个回复吗？如果已经处理好了直接说一声就行，谢谢！🙏"
（若为英文同事："Hey Wang, just checking in on the data report I sent Wednesday — let me know if you've had a chance to look. If it's already handled, a quick heads-up would be great. Thanks!"）

### 🧪 对照表
| 原文 | 改写 | 理由 |
|------|------|------|
| 你为什么不回我 | 想确认一下收到了没 | 假定对方只是忘了，给对方台阶 |
| （无） | 今天下班前能给我个回复吗 | 给出明确 deadline，可执行 |
| （无） | 如果已经处理好了直接说一声 | 降低回复成本，减少心理压力 |
```

### Example 2: 拒绝客户砍价（中英双语）

**用户**: 客户要求打 6 折，我要拒绝但不想丢单。帮我写个委婉拒绝的英文邮件。
**Agent**:

```
### 📧 邮件版（Diplomatic Decline）
**Subject:** Regarding your pricing request for Project Alpha

Hi Sarah,

Thank you for sharing your budget considerations for Project Alpha — we truly appreciate you working with us on this.

After reviewing the scope and our cost structure, I'm afraid a 20% discount isn't something we can offer, as our pricing already reflects the quality and timeline you need. What I can do is offer a 10% discount on the add-on modules if we sign by the end of this month.

Would that work for you? Happy to walk through the details on a call this week.

Best regards,
[Name]

### 🧪 对照表
| 原文 | 改写 | 理由 |
|------|------|------|
| 不可能打6折 | isn't something we can offer | 先谢后拒，立场坚定但不攻击 |
| （无） | What I can do is offer 10% on add-ons | 给替代方案，把谈判转向可行区 |
| （无） | by the end of this month | 制造合理紧迫感 |

### ⚠️ 文化提示
英文语境下 "I'm afraid" 是礼貌拒绝的标准壳，不是示弱；中文版可译为"很遗憾这次确实无法做到"。
```

### Example 3: 道歉邮件（正式版）

**用户**: 我把客户的上线时间搞错了，帮我写一封正式道歉邮件，中文的。
**Agent**:

```
### 📧 邮件版（Apology）
**主题：** 关于项目上线时间安排失误的说明

尊敬的张经理：

非常抱歉，由于我们的内部排期错误，原定于 8 月 30 日的上线时间被安排到了 9 月 6 日，给您和团队造成了不便，在此诚挚道歉。

我们已立即排查流程，确认具体原因是需求评审阶段的时间预估不足，并已补充双人复核机制，确保后续排期不再出现同类问题。

为尽量减少影响，我们可将联调资源从 2 人增至 3 人，争取在 9 月 3 日提前完成。您看这个调整是否可以接受？

再次为此次失误致歉，感谢您的理解。

此致
[Name]

### ✅ 自查
- 认错具体化（排期错误+原因）✓
- 不找借口（"时间预估不足"是原因陈述，非推责）✓
- 补救措施+时限 ✓
```

---

## Common Pitfalls

| 问题 | 解决方案 |
|------|---------|
| 改写过度，原意变了 | 改写前先写一句话"核心诉求"，改完对照检查；只动表达不动事实 |
| 语气用力过猛（礼貌→谄媚） | 用 tone-strength 分级：1-2 微调，3 标准，4-5 重写；默认给 3 并说明 |
| 中文改英文直接逐句翻译 | 按英文沟通习惯重组（直接开头+一句寒暄+明确诉求），不是翻译是重写 |
| 拒绝时只说"No"不给替代 | 永远带替代方案（时间/价格/范围三选一可谈） |
| 道歉变成找借口（"都是因为XX"） | 原因陈述 ≤1 句，且必须是客观事实；重心放在补救 |
| IM 和邮件用同一版本 | 渠道适配：邮件有 subject+落款，IM ≤200 字无落款 |
| 忽略对方文化背景 | 先问/推断受众：日韩更敬语、北欧更直接、美国直接+礼貌、中国微信语境可稍口语 |
| 修改后仍有攻击性残留 | 自查清单逐句过：删除所有"你为什么不/你怎么能"式反问 |

---

## Verification Checklist

- [ ] 核心诉求一句话概括成功，改写后原意保留
- [ ] 危险信号扫描完成，原稿问题已列出
- [ ] 语气模式与受众/场景匹配（已说明选择理由）
- [ ] 若涉英文：已按英文沟通习惯重组，非逐句翻译
- [ ] 拒绝类消息包含替代方案
- [ ] 道歉类消息包含具体补救措施+时限
- [ ] 输出包含对照表（原文/改写/理由）
- [ ] 输出包含渠道适配版本（邮件版或 IM 版）
- [ ] 无攻击性/被动性/模糊性残留

---

## Data Sources & Accuracy

- **语气与文化规范**：基于通用商务沟通惯例（Business correspondence 惯例）与中美职场沟通差异的常识性总结，非权威学术标准；具体公司文化以实际环境为准。
- **英文表达**：模板句式来自常见商务英语用法，建议对重要邮件人工复核。
- **本 skill 不提供法律/合同效力建议**；涉及正式法律或财务承诺的内容应另行审阅。
- 所有处理在本地完成，不依赖外部 API；改写质量取决于输入草稿的信息完整度——草稿越具体（数字、人名、deadline），改写越准。
