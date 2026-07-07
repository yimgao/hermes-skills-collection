---
name: pdf-toolkit
description: "Process PDFs from the terminal — extract text & tables, merge/split/rotate pages, redact sensitive data, fill forms, convert to/from images, add watermarks, and compress. Uses Python (pypdf, pdfplumber, reportlab) with zero system dependencies."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [pdf, documents, extract, merge, split, ocr, forms, redact, utility, office]
    related_skills: [format-converter, screenshot-to-report, file-organizer, csv-explorer]
---

# PDF Toolkit (PDF 工具箱)

> One skill, every PDF operation you actually need — extract text & tables, merge, split, rotate, redact, fill forms, convert to images, add watermarks, and compress. No Adobe, no GUI, no upload to third-party servers.

---

## Overview

PDFs are everywhere in business, legal, and academic work — and most CLI tooling around them is either paid, GUI-only, or requires uploading sensitive documents to random web services. **PDF Toolkit** gives Hermes a self-contained, scriptable PDF workflow that runs entirely on the local machine using pure-Python libraries.

| Capability | What it does |
|------------|--------------|
| **Text Extraction** | Pull plain or structured text from any PDF (with layout preservation option) |
| **Table Extraction** | Extract tabular data from PDFs into CSV / Markdown / JSON |
| **Merge** | Combine multiple PDFs into one, optionally with a table-of-contents page |
| **Split** | Split a PDF by page ranges, by chapter (via bookmark detection), or into N-page chunks |
| **Rotate** | Rotate specific pages or all pages by 90° / 180° / 270° |
| **Redact** | Black-box sensitive text (SSN, credit cards, names) across specified pages |
| **Form Filling** | Fill AcroForm fields programmatically from JSON / YAML / CLI args |
| **Image Conversion** | Convert PDF pages to PNG / JPG / TIFF (single page or range) |
| **PDF Creation** | Build PDFs from text, Markdown, HTML, or images |
| **Watermark** | Stamp text or image watermark on every page |
| **Compression** | Reduce file size by re-saving with lower image quality / removing duplicates |
| **Metadata** | Read & write PDF metadata (title, author, keywords, created date) |
| **Password** | Add / remove PDF password protection |

---

## When to Use

- *"Extract all text from this PDF and save it as a `.txt` file"*
- *"Pull the tables from page 3 of this report into a CSV"*
- *"Merge these 5 PDFs into a single file, in this order"*
- *"Split this 200-page PDF into one file per chapter"*
- *"Rotate page 7 of `contract.pdf` 90° clockwise"*
- *"Redact all instances of my client's name and SSN from this contract"*
- *"Fill out this W-9 form with data from this YAML file"*
- *"Convert the first 10 pages of this PDF to PNG images"*
- *"Create a PDF from this Markdown report"*
- *"Add a 'CONFIDENTIAL' watermark to every page"*
- *"This 50MB PDF is too big — compress it under 10MB"*
- *"Read the title, author, and creation date of this PDF"*
- *"Password-protect this PDF with a 12-character password"*
- *"Extract embedded images from this PDF"*
- *"PDF 怎么转 Word / 怎么把多个 PDF 合并 / 怎么提取里面的表格"*

---

## Core Workflow

### Step 1: Detect the Operation

Parse the user's request and map it to one or more of these canonical operations:

| Trigger words (EN) | 中文 | Operation |
|--------------------|------|-----------|
| extract text, get text, read text, dump | 提取文字、抽取文本、读出 | `extract_text` |
| extract table, pull table, get tables | 提取表格、抽取表格 | `extract_tables` |
| merge, combine, join, concatenate | 合并、拼接 | `merge` |
| split, divide, break apart, chop | 拆分、分割、拆开 | `split` |
| rotate, turn, flip | 旋转、翻转 | `rotate` |
| redact, black out, censor, hide | 打码、涂黑、遮盖 | `redact` |
| fill form, complete form, autofill | 填表、自动填写 | `fill_form` |
| convert to image, render, export as png | 转图片、导出图片、渲染 | `pdf_to_images` |
| create, generate, make pdf from | 生成 PDF、从...创建 | `create` |
| watermark, stamp, brand | 加水印、盖章 | `watermark` |
| compress, shrink, reduce size | 压缩、减小体积 | `compress` |
| metadata, properties, info | 元数据、属性 | `metadata` |
| password, encrypt, lock | 加密、加密码 | `password` |
| extract images, get images, save images | 提取图片、导出图片 | `extract_images` |

If the request is ambiguous, ask: *"Do you want to extract the text, pull the tables, or convert the whole thing to images?"*

### Step 2: Install Required Libraries

Most operations need only 1–2 libraries. Install lazily — only when the operation is invoked:

```bash
# Core (always useful)
pip install pypdf pdfplumber

# For OCR on scanned PDFs
pip install pytesseract pdf2image
# Also requires system tesseract: brew install tesseract

# For creating PDFs from Markdown/HTML
pip install reportlab markdown weasyprint

# For image conversion (requires poppler)
pip install pdf2image
# System: brew install poppler  (macOS) | apt install poppler-utils (Linux)
```

Tell the user upfront which libraries are needed for their requested operation.

### Step 3: Execute the Operation

Below are the **canonical recipes** for each operation. Each is a self-contained Python script that can be run directly or wrapped in a function.

#### 3.1 Text Extraction

```python
from pypdf import PdfReader

def extract_text(path, pages=None, preserve_layout=False):
    reader = PdfReader(path)
    selected = pages or range(len(reader.pages))
    out = []
    for i in selected:
        if i >= len(reader.pages):
            continue
        page = reader.pages[i]
        if preserve_layout:
            # pdfplumber gives better layout
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                out.append(f"=== Page {i+1} ===\n{pdf.pages[i].extract_text()}\n")
        else:
            out.append(f"=== Page {i+1} ===\n{page.extract_text()}\n")
    return "\n".join(out)

# Usage
text = extract_text("report.pdf", pages=range(0, 10))
with open("report.txt", "w") as f:
    f.write(text)
```

**CLI alternative (fastest):**
```bash
# macOS — built-in
textutil -convert txt report.pdf -output report.txt

# Linux — install pdftotext (poppler-utils)
pdftotext -layout report.pdf report.txt
```

#### 3.2 Table Extraction

```python
import pdfplumber, csv, json

def extract_tables(path, page_num=None, output_format="csv", out_path=None):
    """Extract tables from a PDF.
    output_format: 'csv' (single combined file), 'json' (list of dicts), 'md' (markdown)
    """
    tables = []
    with pdfplumber.open(path) as pdf:
        pages = [pdf.pages[page_num]] if page_num is not None else pdf.pages
        for i, page in enumerate(pages):
            page_tables = page.extract_tables()
            for j, t in enumerate(page_tables):
                tables.append({"page": (page_num or i) + 1, "table_index": j, "rows": t})

    if output_format == "json":
        result = json.dumps(tables, ensure_ascii=False, indent=2)
    elif output_format == "md":
        md_lines = []
        for tbl in tables:
            md_lines.append(f"\n### Page {tbl['page']}, Table {tbl['table_index']+1}\n")
            if tbl["rows"]:
                md_lines.append("| " + " | ".join(map(str, tbl["rows"][0])) + " |")
                md_lines.append("| " + " | ".join(["---"] * len(tbl["rows"][0])) + " |")
                for row in tbl["rows"][1:]:
                    md_lines.append("| " + " | ".join(map(str, row)) + " |")
        result = "\n".join(md_lines)
    else:  # csv
        import io
        buf = io.StringIO()
        writer = csv.writer(buf)
        for tbl in tables:
            writer.writerow([f"# Page {tbl['page']}, Table {tbl['table_index']+1}"])
            for row in tbl["rows"]:
                writer.writerow(row)
            writer.writerow([])
        result = buf.getvalue()

    if out_path:
        with open(out_path, "w") as f:
            f.write(result)
        return f"Saved to {out_path} ({len(tables)} tables)"
    return result
```

**When OCR is needed** (scanned PDFs):
```python
# Tell the user: scanned PDFs need OCR
# python -m pip install pytesseract pdf2image
import pytesseract
from pdf2image import convert_from_path

def ocr_pdf(path, lang="eng", dpi=200):
    images = convert_from_path(path, dpi=dpi)
    return "\n\n".join(pytesseract.image_to_string(img, lang=lang) for img in images)
```

#### 3.3 Merge

```python
from pypdf import PdfWriter, PdfReader

def merge_pdfs(input_paths, output_path, insert_toc=False):
    writer = PdfWriter()
    for path in input_paths:
        for page in PdfReader(path).pages:
            writer.add_page(page)

    if insert_toc:
        # Add a blank first page as TOC placeholder
        # (auto-TOC requires more work; usually out-of-scope)
        from pypdf.generic import RectangleObject
        toc_page = writer.add_blank_page(width=595, height=842)
        # Caller can overlay text separately

    with open(output_path, "wb") as f:
        writer.write(f)
    return f"Merged {len(input_paths)} PDFs into {output_path}"
```

**Bash one-liner (when no Python needed):**
```bash
# macOS: use the built-in 'join' via Finder, or 'automator'
# Cross-platform Python:
python -c "from pypdf import PdfWriter, PdfReader; \
w = PdfWriter(); \
[w.add_page(p) for f in ['a.pdf','b.pdf'] for p in PdfReader(f).pages]; \
open('merged.pdf','wb').write(bytes(w))"
```

#### 3.4 Split

```python
from pypdf import PdfReader, PdfWriter

def split_pdf(input_path, output_dir, mode="chunks", chunk_size=1, ranges=None):
    """
    mode='chunks'  → split into N-page chunks (chunk_size each)
    mode='ranges'  → split by explicit page ranges, e.g. [(0,5),(10,15)]
    mode='single'  → one file per page
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    reader = PdfReader(input_path)
    total = len(reader.pages)
    base = os.path.splitext(os.path.basename(input_path))[0]

    if mode == "single":
        plans = [(i, i + 1) for i in range(total)]
    elif mode == "chunks":
        plans = [(i, min(i + chunk_size, total)) for i in range(0, total, chunk_size)]
    elif mode == "ranges":
        plans = ranges  # list of (start_inclusive, end_exclusive)
    else:
        raise ValueError(f"Unknown mode: {mode}")

    written = []
    for idx, (start, end) in enumerate(plans):
        writer = PdfWriter()
        for i in range(start, end):
            writer.add_page(reader.pages[i])
        out = os.path.join(output_dir, f"{base}_p{start+1:04d}-p{end:04d}.pdf")
        with open(out, "wb") as f:
            writer.write(f)
        written.append(out)
    return written
```

#### 3.5 Rotate

```python
from pypdf import PdfReader, PdfWriter

def rotate_pages(input_path, output_path, rotation=90, pages=None):
    """rotation: 90, 180, 270 (clockwise). pages: list of 0-indexed page nums, or None for all."""
    reader = PdfReader(input_path)
    writer = PdfWriter()
    target = set(pages or range(len(reader.pages)))
    for i, page in enumerate(reader.pages):
        if i in target:
            page.rotate(rotation)
        writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)
```

#### 3.6 Redact

```python
import pdfplumber, re
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black
import io

def redact_text(input_path, output_path, patterns, pages=None):
    """
    patterns: list of (label, regex_str) tuples
    Draws a black rectangle over each match.
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()
    target_pages = set(pages or range(len(reader.pages)))

    with pdfplumber.open(input_path) as pdf:
        for i, page in enumerate(reader.pages):
            if i in target_pages:
                plumber_page = pdf.pages[i]
                # Build overlay
                packet = io.BytesIO()
                c = canvas.Canvas(packet, pagesize=(float(page.mediabox.width), float(page.mediabox.height)))
                words = plumber_page.extract_words()
                text_full = plumber_page.extract_text() or ""
                for label, pattern in patterns:
                    for match in re.finditer(pattern, text_full):
                        # Naive: highlight all instances on the page
                        # For real redacting, find the bounding box of each match
                        for w in words:
                            if match.group() in w["text"] or w["text"] in match.group():
                                x0, top, x1, bottom = w["x0"], w["top"], w["x1"], w["bottom"]
                                c.rect(x0, float(page.mediabox.height) - bottom,
                                       x1 - x0, bottom - top, fill=1, stroke=0)
                c.save()
                packet.seek(0)
                from pypdf import PdfReader as PR
                overlay = PR(packet).pages[0]
                page.merge_page(overlay)
            writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)
```

**WARNING: True redaction is hard.** Drawing a black box on top of text is "visual" redaction only — the underlying text can still be extracted. For high-stakes redaction, convert to image first (destroying the text layer), or use a paid tool like Adobe Acrobat Pro's "Redact" feature which actually removes the text. Always verify the redacted PDF with `pdftotext output.pdf -` to confirm sensitive text is gone.

#### 3.7 Fill Forms (AcroForm)

```python
from pypdf import PdfReader, PdfWriter

def fill_form(input_path, output_path, field_values: dict):
    """
    field_values: {"field_name": "value", ...}
    Lists all fields if you pass fields=None.
    """
    reader = PdfReader(input_path)
    if reader.get_fields() is None and field_values is None:
        # List fields
        return {f"/V" if "/T" not in f else f["/T"]: f for f in reader.trailer["/Root"].get("/AcroForm", {}).get("/Fields", [])}

    writer = PdfWriter(clone_from=reader)
    for page in writer.pages:
        writer.update_page_form_field_values(page, field_values)
    # Set NeedAppearances so the filled values render
    if "/AcroForm" in writer._root_object:
        writer._root_object["/AcroForm"].update(
            {pdf_name("/NeedAppearances"): pdf_name("true")}
        )
    with open(output_path, "wb") as f:
        writer.write(f)
    return f"Filled {len(field_values)} fields → {output_path}"

def pdf_name(s):
    from pypdf.generic import NameObject
    return NameObject(s)
```

**First, list available fields** to know what to fill:
```python
reader = PdfReader("w9.pdf")
for field in reader.get_fields().values():
    print(f"{field['/T']}: type={field['/FT']}, current={field.get('/V', 'empty')}")
```

#### 3.8 Convert PDF → Images

```python
from pdf2image import convert_from_path

def pdf_to_images(input_path, output_dir, dpi=200, fmt="png", pages=None):
    """
    pages: list of 1-indexed page numbers, or None for all
    fmt: 'png', 'jpeg', 'tiff'
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    images = convert_from_path(input_path, dpi=dpi, first_page=min(pages) if pages else None,
                               last_page=max(pages) if pages else None)
    saved = []
    base = os.path.splitext(os.path.basename(input_path))[0]
    for i, img in enumerate(images, start=1):
        out = os.path.join(output_dir, f"{base}_p{i:04d}.{fmt}")
        img.save(out, fmt.upper())
        saved.append(out)
    return saved
```

**Requires:** `brew install poppler` (macOS) or `apt install poppler-utils` (Linux)

**Bash alternative:**
```bash
# macOS
sips -s format png report.pdf --out report_page.png   # only first page
# For all pages, use Python
```

#### 3.9 Create PDF from Text / Markdown

```python
# Option A: From plain text
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def text_to_pdf(text, output_path, font="Helvetica", size=11):
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    c.setFont(font, size)
    y = height - 50
    for line in text.split("\n"):
        if y < 50:
            c.showPage()
            c.setFont(font, size)
            y = height - 50
        c.drawString(50, y, line)
        y -= size + 4
    c.save()

# Option B: From Markdown
import markdown
from weasyprint import HTML
from io import StringIO

def md_to_pdf(md_text, output_path, css=None):
    html = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    full_html = f"<html><head><meta charset='utf-8'></head><body>{html}</body></html>"
    HTML(string=full_html).write_pdf(output_path)
```

#### 3.10 Add Watermark

```python
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, red
import io

def add_watermark(input_path, output_path, text="CONFIDENTIAL", opacity=0.3, angle=45):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    # Create a one-page watermark PDF in memory
    packet = io.BytesIO()
    page0 = reader.pages[0]
    w, h = float(page0.mediabox.width), float(page0.mediabox.height)
    c = canvas.Canvas(packet, pagesize=(w, h))
    c.saveState()
    c.translate(w / 2, h / 2)
    c.rotate(angle)
    c.setFont("Helvetica-Bold", 60)
    c.setFillColor(Color(1, 0, 0, alpha=opacity))
    c.drawCentredString(0, 0, text)
    c.restoreState()
    c.save()
    packet.seek(0)
    watermark_page = PdfReader(packet).pages[0]

    for page in reader.pages:
        page.merge_page(watermark_page)
        writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)
```

#### 3.11 Compress

```python
from pypdf import PdfReader, PdfWriter

def compress_pdf(input_path, output_path, image_quality=70):
    """
    Re-saves the PDF with compressed image streams.
    Drops duplicate objects. pypdf does not re-encode JPEGs by default —
    for aggressive compression, use Ghostscript:
        gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
           -dPDFSETTINGS=/ebook -dNOPAUSE -dBATCH \
           -sOutputFile=out.pdf in.pdf
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        page.compress_content_streams()
        # Optionally: iterate through /Resources/XObject and lower JPEG quality
        writer.add_page(page)
    writer.add_metadata(reader.metadata or {})
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path
```

**Bash (best results, requires Ghostscript):**
```bash
# macOS: brew install ghostscript
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
   -dPDFSETTINGS=/ebook -dNOPAUSE -dBATCH \
   -sOutputFile=compressed.pdf original.pdf
# /screen = low quality, /ebook = medium, /printer = high, /prepress = highest
```

#### 3.12 Metadata

```python
from pypdf import PdfReader, PdfWriter
from datetime import datetime

def read_metadata(path):
    reader = PdfReader(path)
    md = reader.metadata or {}
    return {k: str(v) for k, v in md.items()}

def write_metadata(input_path, output_path, **kwargs):
    """kwargs: title, author, subject, keywords, creator, producer"""
    reader = PdfReader(input_path)
    writer = PdfWriter(clone_from=reader)
    from pypdf.generic import TextStringObject
    md = {f"/{k.capitalize()}": TextStringObject(str(v)) for k, v in kwargs.items()}
    writer.add_metadata(md)
    with open(output_path, "wb") as f:
        writer.write(f)
```

#### 3.13 Password / Encryption

```python
from pypdf import PdfReader, PdfWriter

def encrypt_pdf(input_path, output_path, password):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password, algorithm="AES-256")
    with open(output_path, "wb") as f:
        writer.write(f)

def decrypt_pdf(input_path, output_path, password):
    reader = PdfReader(input_path)
    if reader.is_encrypted:
        reader.decrypt(password)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)
```

#### 3.14 Extract Embedded Images

```python
from pypdf import PdfReader
import os

def extract_images(input_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    reader = PdfReader(input_path)
    saved = []
    for i, page in enumerate(reader.pages):
        for j, img in enumerate(page.images):
            ext = img.name.split(".")[-1] if "." in img.name else "bin"
            out = os.path.join(output_dir, f"page{i+1:04d}_img{j+1:03d}.{ext}")
            with open(out, "wb") as f:
                f.write(img.data)
            saved.append(out)
    return saved
```

---

## Example Invocations

### Example 1: Extract tables from a financial report

**User:** "Pull the financial tables from this 10-K PDF (pages 45-60) into CSV"

**Agent action:**
1. Detects `extract_tables` operation
2. Confirms `pdfplumber` is installed: `python -c "import pdfplumber"`
3. Runs:

```python
import pdfplumber, csv

with pdfplumber.open("10k_2024.pdf") as pdf:
    with open("tables.csv", "w", newline="") as out:
        writer = csv.writer(out)
        for i in range(44, 60):  # pages 45-60, 0-indexed
            page = pdf.pages[i]
            for j, table in enumerate(page.extract_tables()):
                writer.writerow([f"# Page {i+1}, Table {j+1}"])
                for row in table:
                    writer.writerow(row)
                writer.writerow([])
```

4. Reports: `✅ Extracted 12 tables from 16 pages → tables.csv (47 KB)`

If the user says "the tables are images, not real tables" — switches to OCR mode and explains the extra setup (`tesseract`, `poppler`).

### Example 2: Merge 5 quarterly reports and add a watermark

**User:** "Merge my Q1–Q4 reports and Q4 update into one PDF, then stamp 'INTERNAL' on every page"

**Agent action:**
1. Confirms file order: `[Q1.pdf, Q2.pdf, Q3.pdf, Q4.pdf, Q4_update.pdf]`
2. Calls `merge_pdfs(...)` → `merged.pdf`
3. Calls `add_watermark("merged.pdf", "merged_final.pdf", text="INTERNAL", opacity=0.25)`
4. Reports file size and page count
5. Suggests: *"Want me to also add a password or set the metadata title to '2024 Quarterly Reports'?"*

### Example 3: Redact a contract for sharing with a vendor

**User:** "I need to send this contract to a vendor, but redact all mentions of 'Acme Corp' and the dollar amount on page 3"

**Agent action:**
1. Warns the user about visual redaction limitations (see Pitfall table)
2. Asks clarification: *"Should I also redact any 10-digit numbers (potential SSNs)?"*
3. Identifies patterns: `["Acme Corp", "\\$\\d{1,3}(?:,\\d{3})*(?:\\.\\d{2})?"]`
4. Runs `redact_text(...)` on page 3
5. **Verification step:** extracts text from output PDF and greps for the patterns to confirm they're gone
6. Reports: *"⚠️ Drawn 4 black boxes on page 3. Verified text extraction no longer contains 'Acme Corp'. For high-stakes redaction, recommend converting page 3 to an image first to destroy the underlying text layer."*

---

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| **`pypdf` can't read scanned/image-only PDFs** | Use `pytesseract` OCR pipeline. Scanned PDFs have no text layer — text "extraction" returns empty strings. Detect by checking `len(page.extract_text())` after extraction. |
| **`pdfplumber` returns empty table for a "table" with merged cells** | Try `table_settings={"vertical_strategy": "text", "horizontal_strategy": "text"}`. Or use `camelot-py` for lattice-based extraction (requires Ghostscript). |
| **Black-box "redaction" leaves text extractable** | Drawing rectangles doesn't remove text. For real redaction: render the page to an image and re-embed, or use Adobe Acrobat Pro's redact tool. Always verify with `pdftotext output.pdf -`. |
| **`pdf2image` fails with "Unable to get page count"** | Poppler not installed. Run `brew install poppler` (macOS) or `apt install poppler-utils` (Linux). |
| **Merged PDF has wrong page order** | Pages are appended in the order given. Verify input file order before merging. |
| **Encrypted PDF can't be read** | Check `reader.is_encrypted` — call `reader.decrypt(password)` first. Empty password = user-password only. |
| **Form has no fillable fields** | Older PDFs may be flat (non-AcroForm). Either overlay text with `reportlab`, or use OCR-based approach to add form fields (advanced). |
| **`pdftotext` not found on Linux** | Install poppler-utils: `sudo apt install poppler-utils` |
| **Created PDF is huge (image-heavy)** | Lower DPI in `pdf_to_images`, or use Ghostscript's `/ebook` or `/screen` setting on the output PDF. |
| **Chinese / CJK characters render as boxes** | Use a CJK-capable font: `c.setFont("STSong-Light", 12)` for ReportLab. For WeasyPrint, install Noto fonts. |
| **Form fields filled but values don't show in PDF viewer** | Need to set `/NeedAppearances: true` on the AcroForm dict so viewers regenerate appearances (see `fill_form` code). |
| **Memory error on large PDFs (1000+ pages)** | Process in chunks of 50-100 pages. Don't load the entire PDF into memory at once. |
| **Rotation produces blank page** | Calling `page.rotate(90)` after adding to writer is too late. Always rotate the page **before** `writer.add_page(page)`. |
| **`pypdf` ImportError after install** | Old code uses `from PyPDF2 import ...`; new versions are `from pypdf import ...`. Both may be installed — uninstall `PyPDF2` to avoid conflicts. |

---

## Verification Checklist

- [ ] Operation correctly identified from user request
- [ ] Required libraries are installed (check with `python -c "import pypdf"`, etc.)
- [ ] System dependencies checked: `poppler` for `pdf2image`, `tesseract` for OCR, `ghostscript` for advanced compression
- [ ] Input file exists and is a valid PDF (`file input.pdf` should say "PDF document")
- [ ] Output directory exists and is writable
- [ ] For merge: page count of output = sum of page counts of inputs
- [ ] For split: total pages of outputs = pages of input
- [ ] For text extraction: output file is non-empty for non-scanned PDFs
- [ ] For OCR: language pack is installed (`tesseract --list-langs` includes target language)
- [ ] For redaction: text re-extracted from output and grep'd to confirm sensitive strings are gone
- [ ] For compression: file size reduction reported (with ratio)
- [ ] For encryption: opening without password fails, opening with password succeeds
- [ ] For form filling: field values present in `reader.get_fields()` after fill
- [ ] For watermark: visual inspection OR `pdfinfo` confirms overlay pages are present
- [ ] Output PDF opens without errors in `PdfReader` (no `PyPDF2.utils.PdfReadError`)

---

## Data Sources & Accuracy

| Source | Purpose | Reliability |
|--------|---------|-------------|
| **pypdf** | Pure-Python PDF read/write, merge, split, rotate, encrypt | High — actively maintained, used by many production tools |
| **pdfplumber** | Text + table extraction with layout | High for text; medium for complex tables (merged cells, multi-line headers) |
| **pdf2image** | PDF → image conversion (wraps poppler) | High — poppler is the gold standard |
| **pytesseract** | OCR (wraps Tesseract) | High for printed text (English); medium for handwriting, CJK, and noisy scans |
| **reportlab** | Programmatic PDF creation from text/shapes | High for simple documents; limited for complex layouts |
| **weasyprint** | HTML/CSS → PDF | High for HTML/CSS fidelity; needs system libraries (pango, cairo) |
| **camelot-py** | Lattice-based table extraction | High for bordered tables; requires Ghostscript |
| **Poppler CLI** (`pdftotext`, `pdfinfo`, `pdftoppm`) | Fast text/image extraction | High — battle-tested C++ library, the basis of most PDF tools |
| **Ghostscript** | Aggressive compression, PDF/A conversion | High — industry standard for print/prepress workflows |

**Limitations:**

- **No library is perfect for tables.** Complex multi-line cells, merged cells, and hierarchical headers are challenging. Always inspect a sample of extracted tables before assuming accuracy.
- **OCR is probabilistic.** For invoices and receipts, expect 85-95% character accuracy on clean scans, lower on photos. Always spot-check critical numbers (totals, dates, account numbers).
- **Visual redaction ≠ real redaction.** Drawing black boxes on top of text leaves the original text extractable. For legal-grade redaction, render to image first or use a specialized tool.
- **Encryption is not DRM.** `pypdf`'s AES-256 encryption prevents casual opening without a password but does not prevent a determined attacker from extracting content via other means. Don't rely on PDF password protection for true confidentiality — use proper file-level encryption (e.g., `gpg`, `age`).
- **PDF/A compliance is hard.** The recipes above produce regular PDFs, not PDF/A (the archival standard). Use Ghostscript with `-dPDFA` for PDF/A conversion.
- **No support for interactive features.** PDF forms with JavaScript, 3D content, multimedia, and digital signatures are not handled by these libraries. Use Adobe Acrobat or specialized libraries (`pyhanko`, `endesive`) for those.
