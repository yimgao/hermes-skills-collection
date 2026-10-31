---
name: backup-audit
description: "Use when you want to know whether your personal data is actually protected — photos, documents, code, tax records, messages — before a disk dies, a laptop is stolen, a folder is deleted by accident, or ransomware hits. Inventories your critical datasets, detects credential files sitting in unencrypted backups, checks whether each dataset has a real destination and a fresh-enough backup, proves the backup is restorable with a test-restore, and scores you against the 3-2-1 rule. Returns a FAIL/PASS coverage table and a pasteable Markdown audit report. Local JSON, stdlib-only, no upload, no account."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [utility, backup, disaster-recovery, data-protection, rpo, rto, 3-2-1, offsite, encryption, restore-test, photos, documents, ransomware, data-loss, cron, local-first, privacy]
    related_skills: [file-organizer, disk-cleanup-advisor, privacy-footprint-cleaner, receipt-vault, renewal-reminder, secret-scanner, password-auditor, lost-item-recovery, moving-relocator, command-journal, website-health-monitor, cron-pipeline-builder]
---

# 🛡️ Backup Audit — 个人数据备份审计器

> You had "a backup." Time Machine ran, and a `~/Backups` folder existed. Then the SSD died on a Tuesday. Restoring gave you **14 months of photos from 2023** and **zero** of 2026. The folder existed. The job had been silently failing on a permission error since a macOS update four months prior.
>
> This skill exists because **a backup you have never restored is a hope, not a backup.** It makes the audit mechanical: what's critical, where it actually goes, how fresh the copy is, whether it contains secrets, and — critically — whether you can *get it back*.

## Overview

| 能力 | 命令 / 触发 | 输出 |
|---|---|---|
| 📦 数据集登记 | `plan --name photos --source ~/Pictures --dest ...` | 每个数据集的源 / 目标 / 频率 / RPO / RTO / 加密状态 |
| 🔍 目录扫描 | `scan <path> --secrets` | 文件数、体积、类型分布、最新/最旧 mtime、凭证文件告警、内容指纹 |
| 📋 覆盖核对 | `cover` | 数据集级 FAIL/PASS 表：源在否、备份在否、备份多旧、是否加密 |
| ✅ 深度校验 | `verify --source --backup [--content]` | 文件数与字节对比；可选逐字节内容哈希比对 |
| ♻️ 试恢复 | `restore --source --backup [--content]` | 恢复到临时目录并逐项对比 —— 唯一能证明「真的能拿回来」的方法 |
| 📝 审计报告 | `report [--out file.md]` | 可粘贴的 Markdown 报告 + 3-2-1 规则检查 + 下一步清单 |
| ⏰ 定时巡检 | `cron_audit.sh` | 每周自动跑 `cover` + `report`，覆盖度退化时非零退出 |
| 🗄️ 数据集目录 | `catalog` | 内置 9 类数据集及其 criticality 评级与理由 |

**核心原则：备份不是「我有副本」，而是「我能在 RTO 内把数据拿回来」。** 每个结论都必须由一次真实校验支撑。

## When to Use

- 硬盘/SSD 发出异响、SMART 报警，或者用了 4 年以上的老机器
- 笔记本被偷 / 家里进水 / 火灾 / 台风前后，想确认还剩下什么
- 刚刚经历了一次误删（`rm -rf` 打错路径、Finder 拖错文件夹）
- 担心勒索软件 —— 它专挑「同步盘里的活文件」下手
- 准备做重大迁移（换机、换 NAS、上云），需要盘点「到底什么东西值得带走」
- 想在报税前确认税务凭证、合同、发票齐全
- 公司要求你证明自己有灾备能力（个人档案 / 自雇者 / 小团队）
- 中文场景：`我的照片备份到底靠不靠谱`、`帮我检查一下备份`、`我的数据能恢复吗`、`做个备份审计`、`勒索软件来了我会不会全没了`

## Core Workflow

### Step 1: 定义「什么丢了会要命」（不要跳过）

先给数据分级。**criticality 3 = 丢了就是灾难，且无法重新下载。**

```bash
S=~/dev/skills/hermes-skills-collection/utility/backup-audit/scripts

# 看内置目录（含每类的理由）
python3 $S/backup_audit.py catalog
```

| 关键性 | 典型内容 | 为什么 |
|---|---|---|
| **3 — 不可再生** | 照片原件、合同、税务记录、身份证扫描件、未推送的代码 | **世上没有第二份。** 丢了就是永久损失 |
| **2 — 麻烦但可再生** | 邮件归档、聊天记录、音乐库 | 重新下载要钱要时间 |
| **1 — 便利性** | 视频、缓存、下载目录 | 重新下载即可 |

登记一个数据集（`--source` / `--dest` 可重复传多个）：

```bash
python3 $S/backup_audit.py plan --name photos \
  --source ~/Pictures \
  --source ~/Desktop/photos-2024 \
  --dest  /Volumes/Backup/photos \
  --dest  ~/Library/CloudStorage/Dropbox/photos \
  --cadence weekly --rpo 7d --rto 4h --encrypted
```

> **criticality 3 且标了 `--encrypted` 之外的任何高关键性数据集，都必须加密。** 未加密的云同步文件夹 = 把你的私钥、`.env`、SSO token 交给同步盘的明文副本。

### Step 2: 扫描源目录，找出「你不知道自己存了什么」

在登记之前先扫一遍真实目录 —— 你通常会发现自己记错了路径，或者漏了一整个数据集。

```bash
python3 $S/backup_audit.py scan ~/Pictures --secrets
```

输出包含：

- **体量与构成** —— 多少文件、多大、什么类型为主（`.jpg×18422`）
- **时间跨度** —— 最新文件几天前？最旧文件什么时候？（**如果最新文件是 90 天前，你的「备份」可能备份的是个空文件夹**）
- **凭证文件告警** —— `.env`、`id_rsa`、`*.pem`、`.netrc`、`.aws/`、`.kube/`、`.git-credentials`
- **内容指纹** —— `91b12fe316b47956`，之后用来证明副本与源一致

> **扫描本身不读取文件内容**，只读文件名、大小、mtime。凭证检测只看**文件名**，不会读取 `.env` 的值。

### Step 3: 核对覆盖度（真实 vs 计划）

```bash
python3 $S/backup_audit.py cover
```

```
Backup coverage  2 dataset(s)

dataset        crit  src    backup    age     enc   status
──────────────────────────────────────────────────────────────────────────────
photos         3     ok     ok        0d      y     PASS
code           3     ok     ok        0d      n     FAIL unencrypted-critical
documents      3     miss   none      -       n     FAIL source-missing,no-destination

──────────────────────────────────────────────────────────────────────────────
1/3 datasets fully covered  2 need action
```

`cover` 会检查这 6 件事，任何一件不过就打 FAIL：

| 检查 | 判定 | 为什么重要 |
|---|---|---|
| 源路径存在 | `src = ok` | 路径写错 = 备份了个寂寞 |
| 目标存在 | `backup ≠ none` | 目标没挂载 / 没创建 = 没有副本 |
| 副本非空 | `backup ≠ empty` | **最常见的失败模式** |
| 副本够新 | `age ≤ 14d` | 30 天前的副本 = 你要恢复一个月的数据 |
| 高关键性已加密 | `enc = y`（criticality 3） | 明文存私钥 = 泄露 |
| 至少 2 个目的地 | 3-2-1 规则 | 挂掉一个盘就全没了 |

**退出码**：0 = 全覆盖，1 = 有数据集需要处理 → 可以直接挂到 cron / CI 上告警。

### Step 4: 深度校验 —— 别相信「有文件」，要相信「字节一样」

文件数对得上不代表内容对得上。一次 `rsync` 中断会留下**同样数量的空文件**。

```bash
# 快速校验：文件数 + 字节数 + 结构指纹
python3 $S/backup_audit.py verify --source ~/Pictures --backup /Volumes/Backup/photos

# 深度校验：逐字节 SHA256（小目录用，最可靠）
python3 $S/backup_audit.py verify --source ~/Pictures --backup /Volumes/Backup/photos --content
```

```
metric                     source         backup  delta
──────────────────────────────────────────────────────────────────────
files                           2              2  +0
bytes                         14B            14B  0B

[OK] file count covers source
content hash  source=5fb96353e9532e4e (2 files)  backup=5fb96353e9532e4e (2 files)
[OK] content hashes MATCH — bytes are identical
```

失败时会明确指出少了几个文件、哈希是否不同。

### Step 5: 试恢复 —— 唯一能证明备份有效的动作

**这一步是本 skill 的核心，也是绝大多数人跳过的一步。** 把备份复制到临时目录，然后跟源对比。临时目录会被自动删除，不会碰你的真实数据。

```bash
python3 $S/backup_audit.py restore --source ~/Pictures --backup /Volumes/Backup/photos --content
```

```
Test restore
  backup  : /Volumes/Backup/photos
  target  : /var/folders/.../restore-test-mfnaj5nn/restored
  source  : /Users/you/Pictures

[OK] restored 18422 files in 12.41s
[OK] restore covers all 18422 source files
[OK] content hash matches source (5fb96353e9532e4e)

  (dry run; temp dir removed)
```

如果源已经没了（模拟全盘故障），也能验证「备份本身能不能独立用」：

```bash
python3 $S/backup_audit.py restore --source ~/Pictures --backup /Volumes/Backup/photos
# [WARN] source missing: /Users/you/Pictures — restoring blind (source should be gone!)
# [OK] source is gone — restore from backup is the only path, and it works
```

### Step 6: 生成报告并挂上定时巡检

```bash
# 可粘贴的 Markdown 报告
python3 $S/backup_audit.py report --out ~/backup-audit-2026.md

# 每周自动巡检（覆盖度退化就非零退出）
bash $S/cron_audit.sh
```

crontab 示例：

```cron
# 每周一 09:12 巡检备份覆盖度
12 9 * * 1 /Users/yimgao/dev/skills/hermes-skills-collection/utility/backup-audit/scripts/cron_audit.sh >> ~/.hermes/backup-audit/cron.log 2>&1

# 每天 03:07 做一次试恢复（小数据集）
7 3 * * * python3 ~/dev/skills/hermes-skills-collection/utility/backup-audit/scripts/backup_audit.py restore --source ~/Documents --backup /Volumes/Backup/documents --content >> ~/.hermes/backup-audit/restore.log 2>&1
```

报告里包含 3-2-1 规则逐条检查：

```
## ⚠️ 3-2-1 rule check

| Rule | Requirement | Status |
|---|---|---|
| 3 copies | every critical dataset has ≥2 destinations (+ the original) — 1/2 | ❌ add a second destination |
| 2 media | ≥1 destination on a different medium (volume / cloud) | ✅ |
| 1 offsite | ≥1 copy away from this machine | ❌ no offsite destination |
```

## Example Invocations

### 例 1：「我的照片备份到底靠不靠谱？」

**User:** `我的照片备份到底靠不靠谱？帮我查一下`

**Agent:**
1. 先扫源目录确认路径和体量：
   ```bash
   python3 $S/backup_audit.py scan ~/Pictures --secrets
   ```
   → 18,422 个文件 / 24.3GB，最新文件 4 天前，最旧 2019 年
2. 登记数据集并指向 Time Machine 卷：
   ```bash
   python3 $S/backup_audit.py plan --name photos --source ~/Pictures \
     --dest /Volumes/TimeMachine/photos --cadence daily --rpo 1d --rto 4h --encrypted
   ```
3. 跑覆盖核对：
   ```bash
   python3 $S/backup_audit.py cover
   ```
   → `photos  3  ok  ok  2d  y  PASS`
4. 试恢复：
   ```bash
   python3 $S/backup_audit.py restore --source ~/Pictures --backup /Volumes/TimeMachine/photos
   ```
   → `[OK] restored 18422 files in 12.41s`
5. 报告结论：
   > 你的照片备份是**有效的** —— Time Machine 卷上确实有 18,422 个文件，试恢复成功。
   > 但只有一个目的地：**Time Machine 挂在同一台机器上，硬盘坏了你一起完蛋。**
   > 下一步：加一个异地目标（Backblaze / 移动硬盘 / NAS），并把 RPO 从 1d 放宽到 7d 能省一半空间。

### 例 2：「勒索软件来了我会不会全没了？」

**User:** `勒索软件来了我会不会全没了？我把重要的东西都放在 Dropbox 里`

**Agent:**
1. 关键判断先行 —— 同步盘**不是备份**。同步会把加密后的文件同步上去，勒索软件一样能拿到密钥。
2. 扫描同步目录找高危文件：
   ```bash
   python3 $S/backup_audit.py scan ~/Documents --secrets
   ```
   → 告警：`.env`（dotenv）、`id_rsa`（ssh-private-key）、`.aws/`（aws-credentials-dir）
3. 登记并标记未加密：
   ```bash
   python3 $S/backup_audit.py plan --name documents --source ~/Documents \
     --dest ~/Library/CloudStorage/Dropbox/Documents --cadence daily
   ```
4. 覆盖核对 → `FAIL unencrypted-critical`
5. 结论：
   > **会全没。** 现在你的布局是「一份明文副本放在云盘上」，勒索软件加密本地文件时会同步上去。
   > 三件事必须做：
   > 1. 备份必须是**版本化/不可变**的（Backblaze、B2、R2、快照），不是文件同步。
   > 2. `.env` / `id_rsa` / `.aws/` 必须**移出**同步目录，且备份侧加密。
   > 3. 加第二个目的地满足 3-2-1，再做一次试恢复确认真的能取回。

### 例 3：「把这份审计报告发给我老板」

**User:** `公司要做数据安全审计，把我的备份现状整理成一份报告`

**Agent:**
```bash
python3 $S/backup_audit.py report --out ~/backup-audit-report.md
```

产出的 Markdown 含：每个数据集的源/目标/体量/频率/RPO/RTO/加密状态、3-2-1 逐条结论、以及按 criticality 排序的「下一步」清单 —— 可直接附在合规材料里。

## Common Pitfalls

| 问题 | 解决方案 |
|---|---|
| **把同步盘当备份** | 同步会传播损坏和加密。真正的备份必须是版本化 / 不可变 / 快照。用 `cover` 检查时把同步盘标成 `dest` 只能算 1 份，不满足 3-2-1 |
| **备份文件数对得上就以为没事** | 一次中断的 rsync 会留下等量空文件。用 `verify --content` 做逐字节比对，或用 `restore` 实测 |
| **Time Machine 只回滚到上个月** | 正常现象，不是 bug。但要确认 `age` 在可接受范围内（RPO 内），而不是「有备份」 |
| **把密钥备份到加密盘，但盘没锁** | `scan --secrets` 会告警。密钥类文件要么不备份，要么只在全盘加密的卷里备份 |
| **`~` 和 `$VAR` 没展开** | 脚本已用 `os.path.expandvars` + `expanduser` 处理，但**手动写路径时最容易写错**。永远用 `cover` 回读一遍 |
| **在同步目录里跑 `scan --secrets` 触发大量 IO** | 先用 `scan` 不带 `--secrets` 看体量；大目录再加 `--secrets` |
| **深层备份要跑很久** | `verify` 默认走结构指纹（采样 300 文件）。`--content` 只在小于 50MB 的目录用 |
| **试恢复覆盖真实数据** | `restore` 只写临时目录并自动删除。**永远不要手动 `cp` 到源路径** |
| **plan.json 权限过松** | 脚本以 `0600` 写入。手动改的话记得 `chmod 600 ~/.hermes/backup-audit/plan.json` |
| **审计报告不含真实文件内容** | 全部基于文件名 / 大小 / mtime / 哈希，**不读取文件正文**。绝不外传 |
| **以为「最近改过文件」= 「备份是新的」** | `age` 取的是目标目录里**所有文件里最新的那个**。若你的备份只同步「改过的文件」，`age` 会骗人 —— 用 `verify` 比对文件数 |
| **criticality 3 用了公共云同步** | 未加密的公共云 = 别人也能读。用 `--encrypted` 标记，并在真实方案里用 crypt/rclone crypt / age 加密后再同步 |

## Verification Checklist

- [ ] 每个关键数据集都已在 `plan` 中登记，`criticality` 评级合理
- [ ] 所有 `source` 路径经 `cover` 确认存在（`src = ok`）
- [ ] 所有 `dest` 路径经 `cover` 确认存在且**非空**（`backup = ok`）
- [ ] 备份年龄在 RPO 之内（`age` 天数 ≤ 你的可接受丢失窗口）
- [ ] 所有 criticality 3 的数据集已标记 `--encrypted`
- [ ] 至少 3-2-1 检查里，「3 copies」和「1 offsite」两项为 ✅
- [ ] 每个 criticality 3 数据集都跑过一次 `restore` 且返回 exit 0
- [ ] 至少一个数据集跑过 `verify --content` 并确认哈希一致
- [ ] `cover` 退出码为 0
- [ ] `report` 已生成并归档（含日期）
- [ ] `cron_audit.sh` 已加入 crontab，且日志文件正在增长
- [ ] 密钥类文件（`.env` / `id_rsa` / `.aws/` / `.netrc`）**不在**未加密的目标里
- [ ] `~/.hermes/backup-audit/plan.json` 权限为 `600`

## Data Sources & Accuracy

| 数据 | 来源 | 准确性说明 |
|---|---|---|
| 文件数、体积 | `os.walk` + `os.lstat` | **精确**。排除 `.git` / `node_modules` / `.venv` / `Library` / `.Trash`（这些目录会严重拖慢扫描并让数字失真） |
| 时间戳 | `st_mtime` | 精确。macOS/Linux 均为 UTC epoch |
| 类型分布 | 文件扩展名 | **近似** —— 无扩展名的文件归为 `(none)`；不检查文件真实 MIME |
| 凭证检测 | **文件名模式匹配** | **只看文件名，不读内容。** 有假阴性（`config.yaml` 里塞了密码不会被发现），也有假阳性（`credentials-notes.md` 会被标成凭证） |
| 内容指纹 | SHA256 over (相对路径, 大小, mtime)，采样 300 文件 | **采样，不是全量。** 能抓住增删改，但理论上可能漏掉采样外的变化。要绝对保证用 `--content` |
| 内容哈希 | 全文件 SHA256 | **精确**，但超过 50MB 自动跳过 |
| 备份新鲜度 | 目标目录中最新文件的 mtime | **有已知偏差** —— 增量同步只传改过的文件，源文件没动时 `age` 会显得很旧。**以 `verify` 的文件数为准** |
| 异地判定 | 路径字符串匹配（`/Volumes/`、`iCloud`、`Dropbox`、`rclone:`、`s3` 等） | **启发式**，不联网探测。人工确认更可靠 |
| 3-2-1 结论 | 依据上述判定 | 规则检查，非合规认证 |

**隐私保证**：本 skill **完全不联网、不上传、不读取文件正文**。所有数据留在 `~/.hermes/backup-audit/plan.json`（权限 600）。除了 `--secrets` 会匹配文件名外，不接触你的内容。

**它不能做的事**：不创建备份（用 `rsync` / `rclone` / Time Machine）、不检测硬盘 SMART 健康度、不加密数据、不恢复被删除的文件（那需要 `photorec` / `testdisk`）、不保证云服务商的数据持久性 SLA。

---

**Files**:
- `scripts/backup_audit.py` —— 主工具（stdlib-only，Python 3.6+）
- `scripts/cron_audit.sh` —— 定时巡检 wrapper
- 存储：`~/.hermes/backup-audit/plan.json`（0600）

**自测**：`python3 scripts/backup_audit.py selftest` —— 18 项断言，覆盖体积换算、目录遍历、凭证检测、指纹稳定性与变更敏感性、内容哈希、恢复等价、路径展开。
