---
name: xiaohongshu-tool
description: "Use when operating on 小红书/Xiaohongshu/RED — search posts, view details, publish notes, comment, like, collect. Uses Hermes's built-in browser tools. Zero Python dependencies."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [xiaohongshu, social-media, browser-automation, content-publishing, rednote]
    related_skills: [xiaohongshu-post-writer, content-repurposer, report-formatter]
---

# 小红书 Browser Tool

> 直接用 Hermes Agent 的浏览器工具操作小红书。搜索、发帖、互动、运营 — 全部通过浏览器完成，零依赖安装。

---

## 与原版 xiaohongshu-skill 的区别

| 维度 | 原版 (DeliciousBuding) | 本版 (Hermes Agent) |
|------|----------------------|-------------------|
| **依赖** | Python + Playwright + Chromium (~300MB) | **零依赖** — 用 Hermes 自带浏览器 |
| **安装** | `pip install` + `playwright install chromium` | **无需安装** — 加载 skill 即可 |
| **内容生成** | 模板引擎（固定模板） | **AI 生成** — LLM 写小红书优化内容 |
| **趋势研究** | 手动搜索 | **自动研究** — 先看热门再创作 |
| **Pipeline** | 独立运行 | **链式集成** — 与 xiaohongshu-post-writer 联动 |
| **文件结构** | 14 个 Python 模块 | **1 个 SKILL.md** |

---

## 前置条件

首次使用需要在浏览器中登录小红书（一次性的，Cookie 会保存）：

```bash
1. 加载本 skill
2. 说 "登录小红书"
3. Hermes 会打开浏览器到小红书登录页
4. 你用微信/小红书 App 扫码登录
5. 之后 Cookie 自动保存，下次不用再登
```

---

## 🔍 功能一：搜索笔记

### 基础搜索
```
User: 在小红书搜 "拉面探店" 的最新图文
Agent:
  1. browser_navigate("https://www.xiaohongshu.com/search_result?keyword=拉面探店&sort=latest&type=general")
  2. browser_console(window.__INITIAL_STATE__.search.feeds)
  3. 提取结果: id, xsec_token, title, likes, collects, comments
  4. 展示给用户
```

### 搜索选项
| 参数 | URL 参数 | 说明 |
|------|---------|------|
| 关键词 | `keyword=` | 搜索词 |
| 排序 | `sort=general/latest` | 综合/最新 |
| 类型 | `type=general/video` | 图文/视频 |
| 时间 | `time_filter=one_day/week/half_year` | 时间范围 |

### 提取数据路径
```
window.__INITIAL_STATE__.search.feeds  → 搜索结果列表
每个 item:
  - id: 帖子 ID
  - xsec_token: 安全令牌（每次会话不同）
  - display_title: 标题
  - liked_count: 点赞数
  - collected_count: 收藏数
  - comment_count: 评论数
  - user.name: 作者名
  - image_list: 图片列表
```

---

## 📄 功能二：帖子详情

```
User: 看这篇帖子的详情，id 是 xxx
Agent:
  1. browser_navigate("https://www.xiaohongshu.com/explore/{id}?xsec_token={token}")
  2. 等待页面加载完成
  3. browser_console(window.__INITIAL_STATE__.note.noteDetailMap)
  4. 提取: 标题、正文、图片、互动数据、评论
  5. 展示给用户
```

### 可选：加载评论
```
browser_console:
  window.__INITIAL_STATE__.note.noteDetailMap[id].note.interactInfo.commentCount
  → 如果有评论，"点击加载更多" → scroll down → 提取评论列表
```

---

## 👤 功能三：用户主页

```
User: 看用户 xxx 的主页
Agent:
  1. browser_navigate("https://www.xiaohongshu.com/user/profile/{user_id}")
  2. browser_console(window.__INITIAL_STATE__.user)
  3. 提取: 昵称、简介、粉丝数、笔记数、笔记列表
```

看自己：
```
browser_navigate("https://www.xiaohongshu.com/user/profile/self")
```

---

## 📝 功能四：发布笔记（核心功能）

### 发布流程（带 AI 内容生成）

```
User: 发一篇小红书，标题和内容你帮我写，关于我在美国做拉面店选址调研的事
Agent:
  1. 先用 AI 生成内容（调用 xiaohongshu-post-writer 流程）
     - 自动生成标题（爆款公式）
     - 自动生成正文（种草风格，600-800字）
     - 自动配 emoji 和排版
     - 自动生成话题标签
  
  2. 展示完整内容给用户确认
     "我准备发以下内容，确认吗？"
     标题: ...
     正文: ...
     标签: ...
  
  3. 用户确认后，打开浏览器发布:
     browser_navigate("https://creator.xiaohongshu.com/publish/publish")
     
  4. 上传图片:
     - 如果是本地图片，告诉用户手動上傳（浏览器安全检查限制自動上傳）
     - 如果是网络图片，先下载再上传
     
  5. 填写标题:
     browser_type → 标题输入框 → 输入标题
     
  6. 填写正文:
     browser_type → 正文输入框 → 输入正文
     
  7. 添加标签:
     browser_click → 添加标签按钮 → 输入标签
     
  8. 用户确认后点击发布
```

### 发布前确认模板

```
📝 即将发布到小红书

━━━━━━━━━━━━━━━━━━
标题：{AI生成的标题}
━━━━━━━━━━━━━━━━━━
{AI生成的正文}
━━━━━━━━━━━━━━━━━━
标签：{标签列表}
图片：{N}张
━━━━━━━━━━━━━━━━━━

请确认：
1️⃣ 内容没问题 → 说"发"
2️⃣ 要修改 → 告诉我要改什么
3️⃣ 取消 → 说"算了"
```

### 图片处理

```
由于浏览器安全限制，上传图片需要你手动选择文件：
1. 我会打开小红书创作者中心的发布页面
2. 你点击"上传图片"按钮，在文件选择器里选图片
3. 选好后我帮你填标题和正文
4. 最后你确认发布

或者你可以先上传图片，我再填文字内容。
```

---

## 💬 功能五：互动（评论/点赞/收藏）

### 评论（带用户确认）
```
User: 评论这篇帖子 xxx，内容你帮我写
Agent:
  1. 查看帖子内容了解语境
  2. 生成 2-3 条评论建议
  3. 展示给用户选择:
     "选一个评论内容:"
     1️⃣ "写得真好！收藏了～"
     2️⃣ "求问这家店在哪里呀？"
     3️⃣ "下次去试试！"
  4. 用户选后:
     browser_navigate("https://www.xiaohongshu.com/explore/{id}?xsec_token={token}")
     browser_click → 评论输入框
     browser_type → 输入评论内容
     browser_click → 发送按钮
     wait 3-5s
  5. 报告结果
```

### 点赞/收藏
```
User: 给这篇帖子点赞
Agent:
  1. 展示帖子信息给用户确认
  2. browser_navigate ... → 找到点赞按钮 → click
  3. 报告结果
```

---

## 📊 功能六：热门趋势研究

```
User: 看看小红书上最近什么拉面内容最火
Agent:
  1. 搜索多个关键词:
     - "拉面 探店" (latest + general)
     - "拉面 推荐" (latest)
     - "拉面 攻略" (most liked)
  
  2. 分析热门帖子的共同特点:
     - 标题模式（数字、emoji、句式）
     - 内容结构（图文vs视频、长度）
     - 互动数据（点赞/收藏/评论比例）
  
  3. 生成趋势报告:
     - 热门标题公式
     - 推荐内容方向
     - 建议发布时间
```

---

## 🤖 功能七：AI 内容 + 发布 Pipeline（最高级用法）

把内容创作和发布串起来：

```
User: 帮我研究一下小红书上最近什么拉面内容火，然后写一篇笔记发出去

Agent 自动执行:
  Phase 1 — 趋势研究
    搜索"拉面 探店"、"拉面 推荐"、"拉面 攻略"
    分析热门内容和标题模式
  
  Phase 2 — AI 内容生成
    用分析结果生成爆款标题 + 正文 + 标签
    展示给用户确认
  
  Phase 3 — 浏览器发布
    打开创作者中心
    引导上传图片
    填写标题 + 正文 + 标签
    确认发布
```

---

## 操作安全规则

以下操作**必须**先展示内容给用户确认，得到明确许可后才执行：

| 操作 | 确认方式 |
|------|---------|
| **发布笔记** | 展示完整标题+正文+图片+标签，用户说"发" |
| **评论** | 展示评论内容，用户选择或确认 |
| **点赞/收藏** | 展示目标帖子信息，用户说"行" |
| **删除/修改** | 展示当前内容，用户确认 |

**禁止：** 任何写操作不能在用户不知情的情况下执行。

---

## 反爬注意事项

小红书反爬比较严格，注意：

1. **操作间隔** — 每次导航/点击后等 3-6 秒
2. **不要连续操作** — 每 5 次操作后等 10-15 秒
3. **验证码检测** — 如果页面跳转到安全验证，提示用户手动过
4. **登录状态** — Cookie 几天到一周过期，过期了需要重新扫码
5. **xsec_token** — 每个会话的 token 不同，从搜索结果拿最新的
6. **频率限制** — 看到"操作频繁"提示就停一下

### 触发验证码了怎么办？
```
1. 等 5-10 分钟
2. 手动打开 https://www.xiaohongshu.com 过验证
3. 重新扫码登录
```

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| **页面加载不出来** | 小红书可能检测到自动化，加随机延迟 |
| **xsec_token 无效** | 重新搜索获取最新的 |
| **登录过期** | 重新扫码登录 |
| **图片上传失败** | 图片太大？检查格式（jpg/png） |
| **发布按钮点不了** | 可能有弹窗或验证，手动操作一次 |

---

## 与原版的对比总结

### 原版做得好（值得学习）
- ✅ 完整的 Python 模块化架构
- ✅ 细致的反爬保护（延迟、频率控制、验证码检测）
- ✅ SOP 编排（自动化工作流）
- ✅ 运营策略管理（配额、日历）

### 本版改进
- ✅ **零安装** — 1 个 SKILL.md，加载即用
- ✅ **AI 内容生成** — LLM 写爆款内容，不是固定模板
- ✅ **趋势研究 Pipeline** — 先研究热门再创作
- ✅ **链式集成** — 与 xiaohongshu-post-writer 联动
- ✅ **更简单** — 不需要懂 Python 就能用
