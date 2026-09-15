---
name: image-prompt-crafter
description: "Craft production-grade prompts for AI image models (Midjourney v6, DALL-E 3, Stable Diffusion XL, Flux, Ideogram) — intent intake, platform-specific syntax, parameter tuning, negative prompts, style/lighting/composition recipes, batch variations, and cost-saving tips. Pairs with prompt-library for storage."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [ai-art, midjourney, dalle, stable-diffusion, flux, prompt-engineering, image-generation, design]
    related_skills: [prompt-library, prompt-refiner, brand-voice-generator, xiaohongshu-post-writer]
---

# Image Prompt Crafter（AI 图像 Prompt 工匠）

> 把"我想要一张好看的图"重写成模型真正能稳定复现的 prompt。覆盖 **Midjourney v6 / DALL-E 3 / SDXL / Flux / Ideogram** 五大主流平台的语法差异、参数调优、负面提示词、风格配方、批量变体生成与成本控制。**它不管存 prompt（那是 prompt-library 的活），也不管文字 prompt 优化（那是 prompt-refiner 的活）——它专攻 AI 图像 prompt。**

| Capability | Description |
|-----------|-------------|
| 🎯 意图澄清 | 5 问澄清法锁定主体/场景/风格/用途/尺寸，避免"AI 自由发挥" |
| 🌐 平台语法 | MJ v6 参数 `--ar --v 6 --style raw`、DALL·E 自然语言、SDXL 权重 `(word:1.3)`、Flux 紧凑描述 — 各自一套规范 |
| 🎨 风格配方 | 摄影/插画/3D/油画/动漫/极简/赛博朋克 — 每种风格的可复用关键词清单 |
| 💡 光影构图 | 黄金分割 / 三分法 / 中心对称 / 伦勃朗光 / 体积光 — 用关键词而非"画好点" |
| 🚫 负面提示 | 针对每个平台写正确的 negative prompt：SDXL 必须、MJ 用 `--no`、DALL·E 内嵌"avoid"语句 |
| 🔁 批量变体 | 一次生成 5-10 个角度/色调/构图变体，对比择优 |
| 💰 成本控制 | DALL·E HD/SDXL local/MJ Fast vs Relax 模式 — 选最便宜的能达到效果的方案 |

---

## When to Use

- *"帮我写一个 Midjourney prompt：赛博朋克霓虹城市夜景"*
- *"我想生成一张小红书封面，要好看、有高级感，能直接商用"*
- *"用 Stable Diffusion XL，画一只蒸汽朋克的猫，需要负提示词去掉畸形手指"*
- *"DALL-E 3 出的图总是太卡通，我要写实摄影风，怎么写 prompt？"*
- *"Flux 模型的 prompt 应该怎么写才最有效？"*
- *"我想批量生成 8 张同一主角不同表情的图像做表情包"*
- *"我有一张参考图，想用 ip-adapter 风格延续，怎么写 prompt？"*
- *"我想做 logo/海报/电商主图/YouTube 缩略图 — 应该选哪个模型 + 怎么写 prompt？"*
- *"给我生成一个 niji 风格的二次元头像 prompt"*
- *"给我一段咒语 / magic words，让我自己跑 MJ"*

---

## Core Workflow

### Step 1: 意图澄清（Intent Intake）—— 5 问必填

**直接写 prompt 通常失败，必须先澄清。** 顺序固定：主体 → 场景/动作 → 风格 → 用途/平台 → 约束。

```markdown
[1] SUBJECT    主体是谁？（人物/动物/物品/场景/抽象概念）
[2] ACTION     在做什么？（静态/动态/表情/姿态）
[3] SETTING    在哪儿/什么环境？（室内/室外/季节/天气）
[4] STYLE      什么风格？（写实摄影/插画/3D/水墨/赛博风…）
[5] OUTPUT     用在哪？（社媒封面/电商主图/头像/海报）+ 比例 + 是否商用
```

**最少必填** = SUBJECT + STYLE + OUTPUT。其它能补则补。

**反面例子** —— *"画一只好看的猫"* ❌ ：主体有了，风格无、构图无、用途无 → 模型自由发挥 → 你 90% 不满意。

### Step 2: 选择目标平台 + 套对应语法

**核心原则：不同平台 prompt 范式差异巨大，不能用一套 prompt 通用。**

| 平台 | 推荐场景 | Prompt 范式 | 关键参数 |
|------|---------|-------------|---------|
| **Midjourney v6** | 艺术性最强 / 概念图 / 商业海报 | 自然语言 + 关键词标签 | `--ar 16:9 --v 6 --style raw --s 250 --q 2` |
| **DALL-E 3** | OpenAI 用户 / 准确理解文字指令 | 完整自然语言段落 | 通过 size + quality (HD/standard) |
| **SDXL / SD3** | 本地部署 / 高度可控 / 商用 | 关键词 + 权重 + 负面提示 | `(word:1.3)` 权重语法，必需 negative prompt |
| **Flux.1 [pro/dev]** | 写实摄影 / 文字渲染 / 真实感 | 紧凑描述句，避免堆砌 | 无权重语法，靠自然语言顺序 |
| **Ideogram 2.0** | 文字/字体渲染 / logo | 自然语言 + 明确文字 | Aspect ratio + style preset |

**判定方法**：用户说 "MJ / Midjourney" → v6 语法；说 "DALL-E / ChatGPT" → DALL·E 3；说 "ComfyUI / 本地 / SD / Stable Diffusion" → SDXL；说 "Flux" → Flux 紧凑描述。

### Step 3: 用 7 段式结构拼装 Prompt

**万能模板（按需删节）**：

```text
[主体描述] + [动作/姿态/表情] + [场景/环境/背景] + [风格] + [光影] + [镜头/构图] + [技术参数]
```

**每一段的关键词清单**：

| 段 | 关键词类别 | 推荐词 |
|----|-----------|--------|
| 主体 | 类别 + 外貌 + 服装 + 配饰 | `a young female chef, freckles, white apron, copper earrings` |
| 动作 | 动词 + 强度 + 视角 | `whisking batter, dynamic pose, looking at camera` |
| 场景 | 地点 + 时间 + 天气 + 季节 | `rustic kitchen, morning light, winter, rain on window` |
| 风格 | 媒介 + 流派 + 时代 | `cinematic photo, Kodachrome 64, 1990s editorial, hyperrealism` |
| 光影 | 主光类型 + 方向 + 色温 | `Rembrandt lighting, soft side light, golden hour, volumetric rays` |
| 镜头 | 焦段 + 视角 + 景深 + 构图 | `85mm portrait lens, f/1.4, shallow DOF, rule of thirds` |
| 技术参数 | 画质 + 平台参数 | `8k, hyperdetailed, Unreal Engine 5 render --ar 4:5 --v 6` |

**黄金顺序**：MJ/Flux 偏好"先主体再环境最后风格"，SDXL 喜欢"风格先行"，DALL·E 适合"段落式叙述"。**顺序错了效果差 30%+。**

### Step 4: 负面提示词（Negative Prompts）—— 防畸形与品牌安全

**适用平台**：SDXL 必需、MJ 推荐（用 `--no`）、Flux 可选、DALL·E 内嵌自然语言。

**通用 negative prompt 模板（SDXL）**：

```text
ugly, deformed, disfigured, extra limbs, missing fingers, mutated hands,
poorly drawn face, bad anatomy, watermark, signature, text, logo,
blurry, low quality, jpeg artifacts, oversaturated,
worst quality, low quality, normal quality
```

**针对场景叠加**：

| 场景 | 额外负面词 |
|------|-----------|
| 人物肖像 | `extra fingers, fused fingers, mutated hands, cross-eyed` |
| 美食 | `moldy, rotten, unappetizing, plastic-looking` |
| 建筑 | `tilted, distorted perspective, floating elements` |
| 品牌安全 | `celebrity likeness, copyrighted character, NSFW` |

**MJ 写法**：把负面词提到 prompt 末尾，用 `--no` 分隔：
```
a serene zen garden --no people, text, watermark, modern buildings
```

### Step 5: 平台特定小技巧（决定成败的细节）

**Midjourney v6**：
- `--style raw` 去掉 MJ 自己的"美化"，更忠实于 prompt
- `--s 250`（stylize）默认 100，升高更艺术、降低更字面
- `--w 0` 权重设为 0 可以"消除"某个元素
- 角色一致性：用 `--cref <image_url>`（character reference），2024 新增
- 风格一致性：用 `--sref <image_url>`（style reference）
- 多人同框：用 `two people :: left: a man :: right: a woman`

**DALL·E 3**：
- 用**完整句子段落**而不是关键词堆砌，效果差异巨大
- 显式说 "Avoid:" + 不想要的东西（DALL·E 没有 negative prompt）
- size 仅支持 `1024x1024 / 1024x1792 / 1792x1024`，自定义比例裁切
- HD 模式 `--quality hd` 算 2 倍 token

**SDXL / ComfyUI**：
- 关键词**权重语法** `(word:1.3)` 控制强调，`(word:0.8)` 弱化
- 推荐 base + refiner 双模型，refiner 加细节
- 步数 30-50，CFG 7-9 是甜蜜区
- 加 LoRA 需在 prompt 中包含触发词 trigger word

**Flux.1**：
- **不要**写"8k, hyperdetailed, masterpiece"这种堆砌词——Flux 已经默认高质
- 紧凑描述（< 75 词）效果 > 长 prompt
- 写实摄影选 `Flux.1 [pro]`，创意艺术选 `[dev]`
- 文字渲染能力远超 MJ/SD——可以直接在 prompt 里写要渲染的文字

**Ideogram 2.0**：
- 文字渲染最强的模型（logo/海报首选）
- 把要渲染的文字用引号包起来：`a poster that says "GRAND OPENING"`
- Style 选择 Realistic / Design / Anime / 3D / Illustration

### Step 6: 批量变体生成（A/B/C 测试）

**同一创意，5 个变体对比**：

| 变体 | 变化维度 | 示例改法 |
|-----|---------|---------|
| A 原版 | 基准 | 主 prompt |
| B 构图 | 镜头/视角 | `wide-angle 24mm, low angle, looking up` |
| C 色调 | 色温/调色 | `cool blue palette, teal and orange grading` |
| D 风格 | 媒介 | `oil painting, thick brushstrokes, impasto` |
| E 时代 | 怀旧/未来 | `1980s film grain, VHS aesthetic` |

**自动化（ComfyUI/MJ batch）**：
```python
# MJ 批量改 style 一键脚本
styles = ["photorealistic", "cinematic", "anime", "oil painting", "watercolor"]
for s in styles:
    print(f'/imagine {base_prompt}, {s} --ar 16:9 --v 6')
```

### Step 7: 成本与重生成策略

| 平台 | 单图成本 | 节省技巧 |
|------|---------|---------|
| MJ Pro | ~$0.04/图 (Fast) / $0.08 (Relax) | 用 `--quality 0.25` 草稿筛，满意再 upscale |
| DALL·E 3 | ~$0.04/图 (standard) / $0.08 (HD) | 标准质量先出，满意再生成 HD |
| SDXL (本地) | 电费 | ComfyUI 跑 batch，本地无限次 |
| Flux (Replicate) | ~$0.05/图 | 先 Pro 再 Dev，避免浪费 |

**重生成决策树**：
```
构图/主体错  → 改 prompt 第 1-3 段，重抽
风格不对    → 改 style 关键词
细节模糊    → 升级 quality / 加 refiner / 加 "8k, sharp focus"
色彩不对    → 改 lighting + palette 关键词
手/眼畸形   → 加 negative prompt，重抽
```

---

## Example Invocations

### 例 1：小红书爆款封面（中文 → MJ v6）

**User**: 我想做一张小红书爆款封面，主题是"自律的早晨"，要高级感、暖色调、有光。

**Agent 流程**：

```
[1] 意图澄清（已满足）
  SUBJECT:  自我提升主题 / 拟人化场景
  ACTION:   早晨仪式
  SETTING:  暖光室内
  STYLE:    写实摄影 + 杂志风
  OUTPUT:   小红书封面 3:4

[2] 平台选择：Midjourney v6（艺术感最强）

[3] 7 段式 prompt：
  a young woman journaling at a sunlit wooden desk at 6am, golden hour light
  streaming through sheer linen curtains, fresh coffee steaming, monstera plant
  in background, shot on 35mm film, Canon EOS R5, soft bokeh, warm color palette
  with muted earth tones, rule of thirds composition, editorial lifestyle
  photography, gentle smile looking down at journal

[4] 负面词 --no：text, watermark, messy desk, phone, screen glow

[5] 参数：--ar 3:4 --v 6 --style raw --s 180

[6] 批量变体（同主题 4 张）：
  - B: 加俯瞰视角 top-down shot
  - C: 冷色调改为深夜版本 cool blue tones, moonlight
  - D: 油画风格 oil painting, thick brushstrokes
  - E: 90s 复古 film grain, kodak gold 200

[7] 建议：先用 --quality 0.25 出 4 张选 best，再 upscale U1-U4
```

**输出 prompt**（用户可直接复制到 MJ）：
```text
/imagine a young woman journaling at a sunlit wooden desk at 6am, golden hour light streaming through sheer linen curtains, fresh coffee steaming, monostra plant in background, shot on 35mm film, Canon EOS R5, soft bokeh, warm color palette with muted earth tones, rule of thirds composition, editorial lifestyle photography, gentle smile looking down at journal --no text, watermark, messy desk, phone, screen glow --ar 3:4 --v 6 --style raw --s 180
```

---

### 例 2：SDXL 电商主图（白底产品图 + 高可控）

**User**: 我卖一款手工皂，要 SDXL 出白底产品主图，电商用，要看上去高级、ins 风。

**Agent 流程**：

```
[1] 输出约束：1024x1024 白底电商主图，ins 极简风

[2] 平台：SDXL + Refiner（成本低、可控性高、本地无限次）

[3] Positive prompt（风格先行）：
  product photography, minimalist, luxury artisan soap bar, fresh sage green
  and cream swirl pattern, smooth matte surface, water droplets on top,
  centered composition, white seamless background, soft studio lighting,
  three-point lighting setup, slight shadow under product, 8k, sharp focus,
  commercial advertising photography, instagram aesthetic
  (clean:1.2) (minimal:1.1) (luxury:1.3)

[4] Negative prompt：
  busy background, patterns, people, hands, text, logo, watermark, shadows
  on background, dirt, fingerprints, low quality, blurry, oversaturated

[5] ComfyUI 推荐参数：
  Steps: 35  CFG: 7.5  Sampler: DPM++ 2M Karras
  Refiner checkpoint: juggernautXL_v9 + sd_xl_refiner_1.0

[6] 批量变体（同样产品，不同 mood）：
  - 暖光版：warm golden side lighting
  - 冷光版：cool studio daylight
  - 俯视图：top-down flat lay, dried flowers around
  - 侧面图：45 degree angle, marble surface

[7] 后期建议：去掉 SDXL 常见色偏 → Photoshop 调色或加 IP-Adapter 风格参考
```

**直接可用 prompt 块**：
```text
Positive:
product photography, minimalist, luxury artisan soap bar, fresh sage green and cream swirl pattern, smooth matte surface, water droplets on top, centered composition, white seamless background, soft studio lighting, three-point lighting setup, slight shadow under product, 8k, sharp focus, commercial advertising photography, instagram aesthetic (clean:1.2) (minimal:1.1) (luxury:1.3)

Negative:
busy background, patterns, people, hands, text, logo, watermark, shadows on background, dirt, fingerprints, low quality, blurry, oversaturated, worst quality
```

---

### 例 3：DALL·E 3 自然语言段落（生成 logo / 海报）

**User**: 帮我用 DALL·E 3 画一张咖啡店开业海报，店名叫"豆语"，要有现代极简感。

**Agent 流程**：

```
[1] 平台：DALL·E 3（嵌在 ChatGPT 里）
[2] 范式：完整段落，不要堆关键词
[3] 文字渲染：DALL·E 3 渲染中文不准 → 用英文店名 + 留中文在后期 PS

[4] 完整 prompt（段落式）：
  A modern minimalist grand opening poster for a specialty coffee shop
  called "BeanSpeak". Composition: a single steaming ceramic cup of
  latte art coffee on a warm beige travertine table, viewed from a
  45-degree top-down angle. The background fades into a soft cream
  gradient. Above the cup, the brand name "BeanSpeak" is displayed in
  elegant serif typography with generous letter spacing. Below the cup,
  the text "GRAND OPENING · JUNE 14" appears in smaller sans-serif.
  Color palette: warm cream, terracotta, deep espresso brown. Lighting:
  soft natural side light from a window. Style: editorial, sophisticated,
  Scandinavian-Japanese fusion aesthetic. Avoid: people, hands,
  cluttered backgrounds, neon colors, photorealistic face, cluttered text.

[5] 输出参数：size 1792x1024（横版海报）, quality hd

[6] 提醒用户：
  - 中文字渲染不可靠，店招"豆语"建议用中文模板后期加
  - 使用 ChatGPT 内置 DALL·E 即可，不需要 API
  - 第一次不满意可微调"color palette"或"lighting"段落
```

---

## Common Pitfalls

| 问题 | 解决方案 |
|------|---------|
| 🎯 "画一只好看的猫"——太模糊，每次结果都不一样 | **5 问澄清法**锁定主体/场景/风格/用途/比例，给具体细节（品种、毛色、姿态、光线） |
| 🌐 同一 prompt 跨平台效果差 3 倍 | **不要复制粘贴**，MJ 用自然语言+参数、SDXL 用权重+负面、Flux 紧凑描述、DALL·E 段落 |
| 📐 主体在画面边缘被裁掉 | 加 `centered composition, subject in middle, full body shot`，避免 `close-up` 与 `--ar` 比例冲突 |
| 🖐️ 人物手/手指畸形 | 加负面词 `extra fingers, mutated hands, bad anatomy`，SDXL 必加，MJ 用 `--no bad hands` |
| 🎨 风格不统一——一会儿写实一会儿插画 | **整段 prompt 只锁定 1 种风格**，"photorealistic" 与 "watercolor" 不能共存 |
| 🔤 中文字渲染乱码（MJ/SDXL 常见） | **MJ/SDXL 不支持中文**：用拼音/英文写；或后期加文字；或换 Ideogram 2.0 / Flux |
| 💸 反复出图烧钱——试错成本高 | 先用最便宜模式（MJ `--q 0.25`、DALL·E standard）出 4 张选 best，再 upscale |
| 🌀 "8k, hyperdetailed, masterpiece" 堆砌词在 Flux 上反效果 | **Flux 不需要这些质量词**，简短描述反而出好图；堆砌反而过饱和 |
| 👥 多人同框分不清 | MJ 用 `::` 分段 `left: a man in blue :: right: a woman in red`，SDXL 加 `(man:1.2) (woman:1.2)` |
| 🏢 商业授权不清 | MJ Pro/Standard 商用 OK；DALL·E 用户有商用权；SDXL 模型需看具体 license（SDXL 商用 OK，部分 checkpoint 限制） |

---

## Verification Checklist

发布/使用前自检：

- [ ] ✅ 已运行 **5 问澄清法**，明确主体/动作/场景/风格/用途
- [ ] ✅ 已根据用户偏好**选择正确平台**（MJ/DALL·E/SDXL/Flux/Ideogram）
- [ ] ✅ Prompt 套用了**该平台专属语法**，不是通用模板
- [ ] ✅ 7 段式结构按需使用，至少包含主体 + 风格 + 参数
- [ ] ✅ **负面提示词**已针对场景编写（SDXL 必加，其它推荐）
- [ ] ✅ **比例 + 画质参数**已设定（`--ar`、`--q`、`--s` 等）
- [ ] ✅ 提供了 **2-5 个变体**（构图/色调/风格/视角/时代）
- [ ] ✅ 给出了**成本控制建议**（草稿模式→upgrade 流程）
- [ ] ✅ 如果用户要**商用**，已提示平台授权情况
- [ ] ✅ 如有**文字渲染**需求，已评估平台能力（Ideogram/Flux > DALL·E > MJ > SDXL）

---

## Data Sources & Accuracy

- **平台版本**：本 skill 基于 Midjourney v6.1 / DALL·E 3 (2024) / SDXL 1.0 / Flux.1 [pro/dev/schnell] / Ideogram 2.0 编写
- **语法规范**：参数名/参数值参考各平台官方文档（docs.midjourney.com / platform.openai.com / stability.ai / blackforestlabs.ai / ideogram.ai）
- **价格**：单图成本为 2024 Q3 估算值，会随平台定价变动；用前请查官方最新价格
- **关键词效果**：基于公开 prompt 社区（PromptHero、Lexica、Civitai）的常见有效组合整理，不是单一来源的"权威配方"
- **更新节奏**：MJ 平均 6 个月一次大版本（v5 → v6），DALL·E 一年一次，Flux 仍快速迭代，建议每年大版本更时回来刷新本 skill
- **风格关键词**：摄影/插画/光影词汇参考摄影教材 + 电影美术词典，非商业截图引用

---

> 💡 **快速上手口诀**：**5 问 → 选平台 → 7 段式 → 加负面 → 出变体 → 选 best → upscale**。重复这个流程 10 次，你就有了自己的 prompt 直觉。
