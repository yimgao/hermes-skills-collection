---
name: image-batch-toolkit
description: "Batch-process images from the terminal — compress, resize, convert (HEIC/WebP/AVIF/PNG/JPG), strip EXIF/GPS, watermark, rename, build contact sheets, and audit folder bloat. Uses Pillow + macOS sips with zero upload."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [images, batch, compress, resize, convert, heic, webp, exif, watermark, thumbnails, utility, photos]
    related_skills: [file-organizer, pdf-toolkit, disk-cleanup-advisor, format-converter, screenshot-to-report]
---

# Image Batch Toolkit (图片批处理工具箱)

> One skill for every image job you actually do — shrink a folder of 300 photos before emailing them, turn iPhone HEICs into shareable JPEGs, strip GPS before posting, generate web thumbnails, or find what's eating your disk. Runs entirely on your machine. **No upload, no cloud, no per-image limits.**

---

## Overview

Phone cameras shoot 4–12 MB per photo, design tools export 30 MB PNGs, and every upload form has a "max 5 MB" ceiling. Most people solve this by dragging files into a random web compressor — which uploads their private photos to a stranger's server. **Image Batch Toolkit** replaces that with a local, scriptable pipeline.

It leans on the best tool for each job: **macOS `sips`** (already installed, zero setup, handles HEIC natively), **Pillow** (Python, cross-platform, fine-grained control), and **`cwebp`** (best-in-class WebP compression).

| Capability | What it does |
|------------|--------------|
| **Compress** | Shrink JPEG/PNG/WebP by 50–90% with quality control and target-size mode |
| **Resize** | Scale by percent, exact dimensions, or longest-edge; smart cover/contain fit |
| **Format Convert** | HEIC → JPG, PNG → WebP, JPG → AVIF, TIFF → PNG, and back |
| **Thumbnails** | Generate square/edge-bounded thumbnails at any size, smart-crop aware |
| **Strip Metadata** | Remove EXIF, GPS location, camera serial, and XMP before sharing |
| **Read Metadata** | Extract camera, lens, ISO, shutter, GPS, and capture date |
| **Watermark** | Stamp text or image watermark, tiled or corner, opacity control |
| **Batch Rename** | Sequential, date-based, or regex rename with collision handling |
| **Contact Sheet** | Build a grid overview of a folder (great for proofing/client review) |
| **Folder Audit** | Find oversized, duplicate, and low-res images; report total bloat |
| **Target-Size Export** | "Make this under 2 MB" — binary-search quality to hit a ceiling |
| **Orientation Fix** | Auto-rotate per EXIF, then bake rotation into pixels |

---

## When to Use

- *"Compress every photo in ~/Pictures/wedding so the folder is under 100 MB"*
- *"Convert all these iPhone HEIC files to JPG for the client"*
- *"Resize these 40 product shots to 1200px wide for the website"*
- *"Strip the GPS location from these photos before I post them"*
- *"Make me 300px square thumbnails of everything in this folder"*
- *"What camera and settings did I use for this photo?"*
- *"Add a '© 2026 Acme' watermark to the bottom-right of all these"*
- *"Rename these to 2026-09-29_001.jpg style"*
- *"Give me a contact sheet of this whole folder so I can pick keepers"*
- *"Which images in this folder are over 5 MB, and what's the total size?"*
- *"This screenshot is 8 MB — get it under 2 MB without visible quality loss"*
- *"Find duplicate images in my Downloads folder"*
- *"Convert this PNG with transparency to WebP"*
- *"这批图太大了，帮我压一下再发邮件" / "把 HEIC 转成 JPG" / "帮我把照片的水印加上"*

### When NOT to use
- Editing/cropping a **single** photo artistically → use a graphics editor; this skill is for batch ops.
- Video files → out of scope (use `ffmpeg`).
- Vector art (SVG, AI, EPS) → use `format-converter` or a vector tool.

---

## Core Workflow

### Step 1: Detect the Operation(s)

Map the user's request to one or more canonical operations. Many requests chain two (e.g. *resize **and** compress*).

| Trigger words (EN) | 中文 | Operation |
|--------------------|------|-----------|
| compress, shrink, reduce size, optimize | 压缩、瘦身、变小 | `compress` |
| resize, scale, make smaller/larger, to Npx | 缩放、调整尺寸、改大小 | `resize` |
| convert, to jpg/webp/heic, format | 转换、转格式、转 JPG | `convert` |
| thumbnail, preview, small version | 缩略图、小图、预览图 | `thumbnail` |
| strip exif, remove gps, remove metadata, clean | 去 EXIF、删定位、清元数据 | `strip_metadata` |
| exif, camera, settings, gps, when taken | 元数据、相机、参数、拍摄时间 | `read_metadata` |
| watermark, stamp, logo, copyright | 水印、盖章、版权 | `watermark` |
| rename, sequential, number them | 重命名、批量改名、编号 | `rename` |
| contact sheet, grid, overview | 联系表、拼图、总览图 | `contact_sheet` |
| audit, largest, how big, duplicates | 审计、最大、多大、重复 | `audit` |
| under N MB, target size, fit limit | 压到 N MB、控制大小 | `target_size` |
| rotate, fix orientation | 旋转、转正 | `fix_orientation` |

**Always confirm the target folder and whether to overwrite originals.** Default policy: **write to a new `_out/` subfolder, never overwrite**.

### Step 2: Establish the Toolchain (lazy — install only what's needed)

```bash
# macOS: sips is preinstalled — HEIC, PNG, JPG, TIFF, raw conversion with zero setup
which sips        # /usr/bin/sips

# Python (cross-platform, the workhorse for anything non-trivial)
pip install Pillow
```

```bash
# Format-specific encoders (optional, best-in-class)
brew install webp          # provides cwebp, dwebp  (WebP — best compression)
brew install imagemagick   # provides magick, convert (fallback swiss-army knife)
brew install libheif       # provides heif-convert   (HEIC on Linux)
brew install exiftool      # provides exiftool       (metadata read/write — most thorough)
brew install oxipng        # lossless PNG optimization
brew install jpegoptim     # lossless JPEG optimization
```

**Setup matrix — what each operation needs:**

| Operation | Minimum | Recommended |
|-----------|---------|-------------|
| compress / resize / convert / thumbnail / strip / watermark / rename / contact sheet | Pillow | + `cwebp` for WebP, + `oxipng`/`jpegoptim` for lossless |
| HEIC input | macOS `sips` (built-in) | `pillow-heif` (`pip install pillow-heif`) on Linux/Win |
| deep metadata | Pillow `.info` | `exiftool` |
| AVIF output | `pillow-avif-plugin` or `magick` | `libavif` (`avifenc`) |

Tell the user upfront which tools are required and offer the one-line install.

### Step 3: Execute the Operation

Each recipe below is self-contained. For anything non-trivial, write a **single editable script** the user can re-run (better than a wall of one-liners).

#### 3.1 Shared helper (include at top of every batch script)

```python
from PIL import Image, ImageOps
from pathlib import Path

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff",
           ".bmp", ".gif", ".heic", ".heif", ".avif"}

def iter_images(folder, recursive=True):
    """Yield image paths, skipping hidden files, _out/, and .thumbnails."""
    p = Path(folder).expanduser()
    glob = p.rglob("*") if recursive else p.glob("*")
    for f in sorted(glob):
        if f.is_file() and f.suffix.lower() in IMG_EXT \
           and not any(part.startswith(("_out", ".")) for part in f.parts[len(p.parts):]):
            yield f

def human(nbytes):
    for unit in ("B", "KB", "MB", "GB"):
        if nbytes < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} TB"

def out_path(src, folder, suffix="", ext=None):
    """Mirror input tree into an output folder, never overwriting originals."""
    dst = Path(folder).expanduser() / src.name
    if ext:
        dst = dst.with_suffix(ext)
    if suffix:
        dst = dst.with_name(dst.stem + suffix + dst.suffix)
    dst.parent.mkdir(parents=True, exist_ok=True)
    return dst
```

#### 3.2 Compress (quality mode + target-size mode)

```python
def compress(src, dst, quality=82, max_edge=None):
    """Rebuild the pixel buffer and re-encode — drops metadata as a side effect."""
    im = ImageOps.exif_transpose(Image.open(src))   # bake orientation
    if max_edge and max(im.size) > max_edge:
        im.thumbnail((max_edge, max_edge), Image.LANCZOS)
    if im.mode in ("RGBA", "P") and dst.suffix.lower() in (".jpg", ".jpeg"):
        im = im.convert("RGB")                      # JPEG has no alpha
    save_kw = {"optimize": True, "progressive": True}
    if dst.suffix.lower() in (".jpg", ".jpeg"):
        save_kw["quality"] = quality
    elif dst.suffix.lower() == ".webp":
        save_kw["quality"] = quality
    im.save(dst, **save_kw)
    return dst

def compress_to_target(src, dst, target_bytes, lo=20, hi=95):
    """Binary-search JPEG/WebP quality to fit under target_bytes."""
    best = None
    size = dst.suffix.lower()
    for _ in range(8):
        q = (lo + hi) // 2
        tmp = dst.with_suffix(".tmp" + dst.suffix)
        compress(src, tmp, quality=q)
        n = tmp.stat().st_size
        if n <= target_bytes:
            best, lo = tmp, q + 1
        else:
            hi = q - 1
            tmp.unlink(missing_ok=True)
        if lo > hi:
            break
    (best or tmp).replace(dst)
    return dst
```

**macOS shortcut (zero Python) — shrink all JPGs in place to a new folder:**
```bash
mkdir -p _out
for f in *.jpg *.JPG *.jpeg; do
  [ -e "$f" ] || continue
  sips -s format jpeg -s formatOptions 82 --resampleWidth 2000 "$f" --out "_out/$f" >/dev/null
done
```

**WebP (best ratio) via cwebp:**
```bash
for f in *.jpg; do cwebp -q 80 -m 6 -metadata none "$f" -o "_out/${f%.jpg}.webp"; done
```

#### 3.3 Resize

```python
def resize(src, dst, width=None, height=None, longest=None, mode="contain"):
    im = ImageOps.exif_transpose(Image.open(src))
    if longest:
        im.thumbnail((longest, longest), Image.LANCZOS)
    elif width and not height:
        r = width / im.width
        im = im.resize((width, round(im.height * r)), Image.LANCZOS)
    elif height and not width:
        r = height / im.height
        im = im.resize((round(im.width * r), height), Image.LANCZOS)
    elif width and height:
        if mode == "cover":     # fill box, center-crop overflow
            im = ImageOps.fit(im, (width, height), Image.LANCZOS)
        else:                   # contain: fit inside box, preserve aspect
            im.thumbnail((width, height), Image.LANCZOS)
    im.save(dst, quality=90)
    return dst
```

**Rules of thumb:** web hero ≤ 2000px, blog inline ≤ 1200px, email ≤ 1600px, retina thumbnails = 2× CSS size.

#### 3.4 Convert (incl. HEIC)

```python
def convert(src, dst):
    im = ImageOps.exif_transpose(Image.open(src))
    if dst.suffix.lower() in (".jpg", ".jpeg") and im.mode in ("RGBA", "P"):
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.convert("RGBA").split()[-1])
        im = bg
    im.save(dst)
    return dst
```

**HEIC without any Python dependency (macOS):**
```bash
for f in *.HEIC *.heic; do
  [ -e "$f" ] || continue
  sips -s format jpeg -s formatOptions 90 "$f" --out "_out/${f%.*}.jpg" >/dev/null
done
# Bulk PNG→JPG, TIFF→PNG, etc. — sips auto-detects: -s format <jpeg|png|tiff|gif>
```

**HEIC on Linux/Windows:**
```bash
pip install pillow-heif      # registers a HEIF opener with Pillow
# then: import pillow_heif; pillow_heif.register_heif_opener()
```

#### 3.5 Thumbnails

```python
def thumbnail(src, dst, size=300, square=True, quality=85):
    im = ImageOps.exif_transpose(Image.open(src))
    if square:
        im = ImageOps.fit(im, (size, size), Image.LANCZOS, centering=(0.5, 0.5))
    else:
        im.thumbnail((size, size), Image.LANCZOS)
    if im.mode != "RGB":
        im = im.convert("RGB")
    im.save(dst, quality=quality, optimize=True)
    return dst
```

#### 3.6 Strip Metadata (privacy)

```python
def strip_metadata(src, dst, keep_orientation=True):
    """Re-encode WITHOUT copying EXIF/XMP/GPS. If keep_orientation, bake rotation into pixels first."""
    im = Image.open(src)
    if keep_orientation:
        im = ImageOps.exif_transpose(im)
    clean = Image.new(im.mode, im.size)      # brand-new image = no metadata
    clean.putdata(list(im.getdata()))
    clean.save(dst)
    return dst
```

**Verify removal (must return nothing):**
```bash
exiftool -GPSPosition -DateTimeOriginal -Model _out/photo.jpg   # if exiftool installed
# Fallback: python -c via a small script — Pillow returns {} for exif after strip
```
> ⚠️ Simply re-saving with Pillow (`im.save(dst)`) **keeps** EXIF in many versions. Use the metadata-free rebuild above, or `exiftool -all= -overwrite_original file.jpg`.

#### 3.7 Read Metadata

```python
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def read_metadata(src):
    im = Image.open(src)
    out = {"format": im.format, "size": im.size, "mode": im.mode}
    exif = im.getexif()
    if exif:
        for k, v in exif.items():
            out[TAGS.get(k, k)] = v
    # GPS (nested IFD)
    if exif and (gps := exif.get_ifd(0x8825)):
        out["GPS"] = {GPSTAGS.get(k, k): v for k, v in gps.items()}
        out["_has_gps"] = True
    return out
```

**CLI (much richer — recommended when available):**
```bash
exiftool photo.jpg
exiftool -GPSPosition -DateTimeOriginal -Make -Model -LensModel -ISO -FNumber -ExposureTime photo.jpg
```

**Non-Python fallback (macOS built-in):**
```bash
mdls -name kMDItemAcquisitionModel -name kMDItemPixelWidth photo.jpg
sips -g pixelWidth -g pixelHeight -g format photo.jpg
```

#### 3.8 Watermark

```python
from PIL import Image, ImageDraw, ImageFont

def watermark(src, dst, text="© 2026 Your Name", pos="br",
              opacity=140, tiled=False, font_size=None):
    im = Image.open(src).convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    fs = font_size or max(18, im.width // 28)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", fs)
    except OSError:
        font = ImageFont.load_default()
    fill = (255, 255, 255, opacity)
    if tiled:
        step_x, step_y = fs * 14, fs * 6
        for y in range(0, im.height, step_y):
            for x in range(0, im.width, step_x):
                d.text((x, y), text, font=font, fill=fill)
    else:
        box = d.textbbox((0, 0), text, font=font)
        tw, th = box[2] - box[0], box[3] - box[1]
        x, y = {"br": (im.width - tw - 20, im.height - th - 20),
                "bl": (20, im.height - th - 20),
                "tr": (im.width - tw - 20, 20),
                "tl": (20, 20)}[pos]
        d.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, opacity))  # shadow
        d.text((x, y), text, font=font, fill=fill)
    Image.alpha_composite(im, ov).convert("RGB").save(dst)
    return dst
```

**Image-logo variant:** open the logo, `resize` to ~12% of width, `.putalpha()` a scaled alpha, then `im.paste(logo, (x, y), logo)`.

#### 3.9 Batch Rename

```python
from datetime import datetime
import re

def batch_rename(folder, pattern="{date}_{n:03d}", start=1, dry_run=True):
    """pattern tokens: {date} {datetime} {n} {stem} {name}. dry_run prints the plan."""
    imgs = list(iter_images(folder, recursive=False))
    plan = []
    for i, src in enumerate(imgs, start=start):
        m = re.search(r"(\d{4})[:-](\d{2})[:-](\d{2})", src.name)
        date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else \
               datetime.fromtimestamp(src.stat().st_mtime).strftime("%Y-%m-%d")
        new = pattern.format(date=date, datetime=datetime.now().strftime("%Y%m%d-%H%M%S"),
                             n=i, stem=src.stem, name=src.name)
        dst = src.with_name(new + src.suffix.lower())
        if dst != src:
            plan.append((src, dst))
    if dry_run:
        for a, b in plan:
            print(f"{a.name}  →  {b.name}")
        return plan
    for a, b in plan:
        b = _dedupe(b)                 # avoid clobbering
        a.rename(b)
    return plan

def _dedupe(p):
    n, cand = 1, p
    while cand.exists():
        cand = p.with_name(f"{p.stem}_{n}{p.suffix}")
        n += 1
    return cand
```

> **Always `dry_run=True` first.** A bad rename of 2,000 photos is painful to reverse.

#### 3.10 Contact Sheet

```python
def contact_sheet(folder, dst, cols=6, cell=300, padding=8, label=True):
    imgs = list(iter_images(folder))
    if not imgs:
        raise SystemExit("No images found.")
    rows = (len(imgs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (cell + padding) + padding,
                              rows * (cell + padding) + padding), (28, 28, 30))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except OSError:
        font = ImageFont.load_default()
    for idx, src in enumerate(imgs):
        r, c = divmod(idx, cols)
        x = padding + c * (cell + padding)
        y = padding + r * (cell + padding)
        im = ImageOps.fit(ImageOps.exif_transpose(Image.open(src)).convert("RGB"),
                          (cell, cell), Image.LANCZOS)
        sheet.paste(im, (x, y))
        if label:
            d.text((x + 2, y + cell - 16), src.name[:34], font=font, fill=(230, 230, 230))
    sheet.save(dst, quality=88)
    return dst
```

#### 3.11 Folder Audit (largest / duplicates / low-res)

```python
import hashlib
def audit(folder, big_mb=5, lowres_px=800):
    imgs = list(iter_images(folder))
    total = sum(f.stat().st_size for f in imgs)
    rows, hashes = [], {}
    for f in imgs:
        kb = f.stat().st_size
        w = h = 0
        try:
            with Image.open(f) as im:
                w, h = im.size
        except Exception:
            pass
        hkey = hashlib.md5(f.read_bytes()).hexdigest()
        hashes.setdefault(hkey, []).append(f)
        rows.append((f, kb, w, h))
    big = sorted(rows, key=lambda r: -r[1])[:20]
    dupes = [v for v in hashes.values() if len(v) > 1]
    lowres = [r for r in rows if r[1] and max(r[2], r[3]) < lowres_px]
    print(f"{len(imgs)} images · {human(total)} total")
    print(f"\nTop 20 largest:")
    for f, kb, w, h in big:
        print(f"  {human(kb):>9}  {w}x{h}  {f.name}")
    if dupes:
        print(f"\n{len(dupes)} duplicate group(s) (identical bytes):")
        for g in dupes:
            print("  • " + "  ==  ".join(p.name for p in g))
    if lowres:
        print(f"\n{len(lowres)} low-res (<{lowres_px}px) — candidates for deletion/upscale")
    return {"count": len(imgs), "total": total, "big": big, "dupes": dupes, "lowres": lowres}
```

#### 3.12 Fix Orientation

```python
def fix_orientation(src, dst):
    """Bake EXIF orientation into pixels, then save without the rotation tag."""
    im = ImageOps.exif_transpose(Image.open(src))
    im.save(dst)
    return dst
```

### Step 4: Run, Report, and Offer the Next Step

After running a batch, always report a **before/after card**:

```
✅ Processed 148 images
   Before: 412.6 MB  →  After: 63.2 MB  (84.7% smaller)
   Output: ~/Pictures/wedding/_out/   (originals untouched)
   Skipped: 0 (all images had valid data)
   Largest result: IMG_2287.jpg  4.8 MB → 0.9 MB
```

Then offer chained next steps:
- *"Want me to strip GPS from these before you share them?"*
- *"Should I generate 400px thumbnails for the picker page?"*
- *"I can build a contact sheet so you can spot the blurry ones."*

### Complete runnable script (compress a folder end-to-end)

```python
#!/usr/bin/env python3
"""batch_compress.py SRC_DIR [--max-edge 2000] [--quality 82] [--target-mb 2]"""
import sys, argparse
from pathlib import Path
from PIL import Image, ImageOps

def human(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024: return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} TB"

def compress_file(src, dst, quality, max_edge, target_bytes=None):
    im = ImageOps.exif_transpose(Image.open(src))
    if max_edge and max(im.size) > max_edge:
        im.thumbnail((max_edge, max_edge), Image.LANCZOS)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    q = quality
    def save(q):
        im.save(dst, quality=q, optimize=True, progressive=True)
    save(q)
    if target_bytes:
        lo, hi = 20, q
        for _ in range(7):
            if dst.stat().st_size <= target_bytes: break
            hi = q; q = (lo + hi) // 2; save(q)
    return dst

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--out", default=None)
    ap.add_argument("--max-edge", type=int, default=2000)
    ap.add_argument("--quality", type=int, default=82)
    ap.add_argument("--target-mb", type=float, default=None)
    a = ap.parse_args()
    src_dir = Path(a.src).expanduser()
    out_dir = Path(a.out).expanduser() if a.out else src_dir / "_out"
    out_dir.mkdir(parents=True, exist_ok=True)
    exts = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".heic", ".bmp"}
    files = [f for f in sorted(src_dir.rglob("*")) if f.suffix.lower() in exts and "_out" not in f.parts]
    before = sum(f.stat().st_size for f in files)
    tb = int(a.target_mb * 1024 * 1024) if a.target_mb else None
    done = 0
    for f in files:
        rel = f.relative_to(src_dir)
        dst = out_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            compress_file(f, dst, a.quality, a.max_edge, tb)
            done += 1
        except Exception as e:
            print(f"[WARN] {f.name}: {e}")
    after = sum(p.stat().st_size for p in out_dir.rglob("*") if p.is_file())
    pct = (1 - after / before) * 100 if before else 0
    print(f"✅ {done}/{len(files)} images → {out_dir}")
    print(f"   {human(before)} → {human(after)}  ({pct:.1f}% smaller)")

if __name__ == "__main__":
    main()
```

Usage:
```bash
python batch_compress.py ~/Pictures/wedding --max-edge 2000 --quality 80
python batch_compress.py ./shots --target-mb 2          # every file ≤ 2 MB
```

---

## Example Invocations

### Example 1: Shrink a photo folder for email

**User:** *"This folder of wedding photos is 400 MB and Gmail won't take it. Get it small enough to send."*

**Agent action:**
1. Runs `audit(folder)` → reports `148 images · 412.6 MB`, top offenders, `0 duplicates`.
2. Confirms targets: *"I'll cap the long edge at 2400px and quality 80, output to `_out/`. Sound good?"* (proceeds on the sensible default if no reply).
3. Writes `batch_compress.py` to the folder, runs it.
4. Reports:
   ```
   ✅ 148/148 images → wedding/_out
      412.6 MB → 61.4 MB  (85.1% smaller)  — fits a 25 MB-per-file Gmail limit easily
   ```
5. Offers: *"Want a contact sheet, or should I zip it into one attachment?"*

### Example 2: HEIC → JPG + strip GPS before posting

**User:** *"These iPhone photos are HEIC and have my home address in the GPS. I need JPGs with no location data for my listing."*

**Agent action:**
1. Detects `convert` + `strip_metadata`.
2. Uses `sips -s format jpeg` (macOS, no install) to convert, then the metadata-free rebuild to strip.
3. **Verifies** with `exiftool -GPSPosition _out/*.jpg` → prints nothing → confirms compliance.
4. Reports `✅ 32 HEIC → JPG, EXIF/GPS stripped & verified. Output: ./_out/`.

### Example 3: Web thumbnails + on-the-fly audit

**User:** *"I have 60 product shots. Make me 400px square thumbnails for the grid, and tell me which originals are too small to use."*

**Agent action:**
1. Runs `thumbnail(src, dst, size=400, square=True)` over all 60 → `_out/thumbs/`.
2. Runs `audit(folder, lowres_px=1200)` → flags 4 images under 1200px.
3. Reports: *"✅ 60 thumbnails at 400×400. ⚠️ 4 originals are under 1200px (IMG_0031 is 640px) — too soft for a hero image; want me to upscale or regroup them?"*

---

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| **JPEG save fails on a PNG with transparency** (`cannot write mode RGBA as JPEG`) | Convert first: `im.convert("RGB")`, or composite onto a white background (see `convert()` recipe). |
| **Photo looks rotated 90° after resize** | Pillow reads EXIF orientation as a tag but doesn't apply it. Always wrap with `ImageOps.exif_transpose(im)` **before** any resize/save. |
| **EXIF/GPS still present after `im.save()`** | Pillow preserves EXIF on round-trips. Use the metadata-free rebuild (new `Image` + `putdata`), or `exiftool -all= -overwrite_original`. Verify with exiftool. |
| **HEIC file raises "cannot identify image file"** | Pillow can't read HEIC by default. Use macOS `sips`, or `pip install pillow-heif` + `pillow_heif.register_heif_opener()`. |
| **`quality=90` produces a *bigger* PNG** | PNG is lossless — `quality` doesn't shrink it. Convert to JPEG/WebP, or run `oxipng`/`pngquant`. |
| **Animated GIF becomes a single frame** | Pillow flattens on save. For GIF/WebP animation, iterate frames (`im.seek`, `im.convert("RGBA")`) and pass `save_all=True, append_images=[...]`. |
| **Transparent PNG turned black in WebP/JPEG** | Alpha lost. For JPEG, composite on white; for WebP use lossless (`-lossless`) to keep alpha. |
| **Real photos compress fine, screenshots barely shrink** | Screenshots are flat-color already — JPEG is the wrong codec. Use PNG + `oxipng`, or WebP lossless. Expect 10–20%, not 80%. |
| **Colors shifted after converting CMYK TIFF/JPEG** | Convert the color space: `im.convert("RGB")` (Pillow handles CMYK→RGB but check a sample; use `ImageCms` for accurate ICC transforms). |
| **`sips` silently overwrites the original** | `sips file.jpg -s ... ` edits in place! Always pass `--out newpath.jpg` to write elsewhere. |
| **Batch crashes partway, some files processed** | Always write to `_out/` (never overwrite originals) so a crash is non-destructive. Catch per-file exceptions and log `[WARN]`. |
| **Output folder included as input → infinite reprocessing** | `iter_images` must skip `_out/` and hidden dirs (the shared helper does). |
| **Memory blow-up on 100 MP / RAW images** | Use `Image.open(...).draft("RGB", (2000, 2000))` to decode at reduced size for JPEGs; process one at a time; never `list()` full pixel data across thousands of files. |
| **Renamed 2,000 photos and lost the mapping** | Always dry-run first; keep the printed plan; optionally write a `rename_manifest.csv` of old→new. |
| **Two files hash-identical but different names flagged as duplicates** | `audit` compares raw bytes — that's true duplicates. If you want *visual* duplicates, compare perceptual hashes (`imagehash` library). |

---

## Verification Checklist

- [ ] Operation(s) correctly identified from the user's request (and confirmed with the user when destructive)
- [ ] Toolchain present: `which sips` (macOS) and/or `python -c "import PIL"`; install only what's needed
- [ ] Input folder exists and contains images (`iter_images` returns > 0)
- [ ] Output goes to `_out/` — **originals never overwritten**
- [ ] EXIF orientation applied (`ImageOps.exif_transpose`) before resize/compress
- [ ] Alpha handled when writing JPEG (composited or converted to RGB)
- [ ] For metadata strips: re-read output with `exiftool`/Pillow and confirm GPS/EXIF is gone
- [ ] For target-size: final file size ≤ requested ceiling (verified with `stat`)
- [ ] For rename: dry-run plan reviewed before executing; collision `_1` suffixes applied
- [ ] Before/after size report produced (`human()` bytes + % reduction)
- [ ] Failed files logged, not silently dropped
- [ ] Sample outputs visually spot-checked (at least the largest)

---

## Data Sources & Accuracy

| Tool / Source | Purpose | Reliability |
|---------------|---------|-------------|
| **Pillow (PIL)** | Cross-platform decode/encode, resize, crop, draw, EXIF read | High — the Python imaging standard; handles 30+ formats |
| **macOS `sips`** | Zero-install convert/resize on macOS, native HEIC support | High for common conversions; limited flags vs Pillow |
| **`cwebp` / `dwebp` (libwebp)** | Best-in-class WebP encode/decode | High — Google's reference encoder |
| **`exiftool`** | Most thorough metadata read/write, including GPS | High — the definitive metadata tool |
| **`oxipng` / `jpegoptim` / `pngquant`** | Lossless/near-lossless optimization | High — safe re-encoders |
| **`libheif` / `pillow-heif`** | HEIC/HEIF support off macOS | High for decode; encode support varies |
| **`imagehash`** (optional) | Perceptual (visual) duplicate detection | High for near-dupes; needs `pip install imagehash` |

**Limitations:**
- **Lossy compression is irreversible.** Always keep originals; never run a compress loop over already-compressed files.
- **Metadata stripping is all-or-nothing with the rebuild method** — it removes copyright, too. If you need to keep *some* fields, use `exiftool` with explicit `-TagsFromFile`.
- **Perceptual duplicates need a perceptual hash.** Byte-identical detection misses re-saved/resized copies.
- **RAW files** (CR2, NEF, ARW) need `rawpy` or `libraw` — not covered by the stdlib recipes here.
- **Color management is shallow.** Pillow converts CMYK→RGB but does not apply ICC profiles on save; for print-accurate color use `ImageCms` or `magick`.
- **No image *editing*.** This is batch mechanics (resize/convert/strip/watermark), not retouching — no healing, layers, or curves.

---

**Local-first guarantee:** every operation runs on your machine. Nothing is uploaded to any server. Safe for private photos, IDs, medical images, and client work under NDA.

