---
name: disk-cleanup-advisor
description: "Use when diagnosing disk space issues — scans drive usage, identifies large files, caches, and duplicate files, and suggests safe cleanup actions."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [disk, cleanup, storage, utility, macos, maintenance]
    related_skills: [file-organizer]
---

# Disk Cleanup Advisor

> Diagnose disk space issues. Scans drive usage, finds large files, caches, downloads folders, and duplicate files — then suggests safe cleanup actions.

---

## When to Use

- *"My Mac is running out of space — help me clean up"*
- *"What's taking up all my disk space?"*
- *"Find large files I can delete safely"*
- *"帮我清理磁盘空间"*

---

## Core Workflow

### Step 1: Scan Disk Usage

```bash
# Overall usage
df -h /

# Largest directories (home)
du -sh ~/*/ | sort -rh | head -20

# Largest files
find ~ -type f -size +100M -exec ls -lh {} \; 2>/dev/null | sort -k5 -rh | head -20
```

### Step 2: Identify Cleanup Targets

| Category | Common Culprits | Safe to Delete? |
|----------|----------------|-----------------|
| **Downloads** | Old .dmg, .zip, .pkg | ✅ Yes if already used |
| **Trash** | Deleted files | ✅ Yes |
| **Caches** | ~/Library/Caches/* | ✅ Yes (will rebuild) |
| **Xcode** | DerivedData, iOS DeviceSupport | ✅ Yes |
| **node_modules** | Past project dependencies | ✅ Yes (can reinstall) |
| **Docker** | Unused images, containers | ✅ Yes (docker system prune) |
| **Podfile** | CocoaPods cache | ✅ Yes |
| **.venv** | Old virtual environments | ✅ Yes (if project done) |

### Step 3: Generate Report

```markdown
# Disk Cleanup Report

**Drive:** Macintosh HD
**Used:** {N}GB / {N}GB ({N}% full)

---

## 🔴 Top Space Hogs
| Path | Size | Type | Action |
|------|------|------|--------|
| ~/Downloads | {N}GB | Mixed | Review |
| ~/Library/Caches | {N}GB | Cache | ✅ Safe to delete |
| ~/dev/old-project/node_modules | {N}GB | Deps | ✅ Can remove |

## 📋 Recommended Actions

1. `rm -rf ~/Library/Caches/*` — frees {N}GB
2. `docker system prune -a` — frees {N}GB
3. Review ~/Downloads — {N} items untouched >30 days
4. Delete old Xcode DerivedData — frees {N}GB

## 💾 Potential Space Recovery
| Action | Est. Recovery |
|--------|---------------|
| Clear caches | {N}GB |
| Remove old projects | {N}GB |
| Clean Docker | {N}GB |
| Empty Trash | {N}GB |
| **Total** | **{N}GB** |
```
