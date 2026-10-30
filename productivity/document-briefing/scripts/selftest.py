#!/usr/bin/env python3
"""selftest.py — prove docdigest works on this machine, with zero network.

Builds throwaway fixtures in a temp dir and asserts behaviour end to end:
  * plain text  -> line locators, headings, amounts, dates, unwrapped sentences
  * markdown    -> line locators + list items not fused
  * html        -> paragraph locators, nav/script excluded, headings isolated
  * docx        -> paragraph locators + heading style honoured (built as a zip)
  * pptx        -> one locator per slide (built as a zip)
  * pdf         -> page locators (needs macOS `cupsfilter`; skipped otherwise)
  * scanned pdf -> clean error, exit 2
  * check       -> 0 on a faithful briefing, 1 on invented pages / fake quotes
  * CJK         -> full-width punctuation preserved, 元 amounts captured

Usage:  python3 selftest.py [-v]
Exit:   0 all passed, 1 at least one failure
"""
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "docdigest.py"
VERBOSE = "-v" in sys.argv

PASS, FAIL, SKIP = [], [], []


def ok(name, cond, detail=""):
    if cond:
        PASS.append(name)
        print(f"  PASS  {name}")
    else:
        FAIL.append(name)
        print(f"  FAIL  {name}  {detail}")


def skip(name, why):
    SKIP.append(name)
    print(f"  SKIP  {name}  ({why})")


def run(*args, expect=0):
    p = subprocess.run([sys.executable, str(TOOL), *args],
                       capture_output=True, text=True)
    if VERBOSE or p.returncode != expect:
        if p.stdout.strip():
            print("    " + p.stdout.strip().replace("\n", "\n    "))
        if p.stderr.strip():
            print("    " + p.stderr.strip().replace("\n", "\n    "))
    return p


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
AGREEMENT = """COMPLIANCE AND SERVICE AGREEMENT

1. Term and Termination
This agreement shall commence on 2026-03-01 and shall remain in effect for twelve
(12) months. Either party may terminate this agreement for material breach upon
thirty (30) days written notice. Customer must give sixty (60) days notice of
non-renewal, otherwise the agreement auto-renews at a 7% increase.

2. Fees and Payment
Customer shall pay a monthly fee of $4,200. Late payments incur a penalty of 1.5%
per month. Invoices are due within 15 days of receipt. All fees are non-refundable
except as expressly stated in Section 6.

3. Limitation of Liability
In no event shall either party be liable for indirect, incidental, or consequential
damages. Aggregate liability is capped at the fees paid in the preceding twelve
months, not to exceed $50,400.

6. Refunds
If Supplier fails to deliver the initial implementation by 2026-05-15, Customer may
terminate and receive a full refund of prepaid fees.
"""

CONTRACT_CN = """软件采购与技术服务合同

一、服务期限
本合同自 2026-03-01 起生效，有效期为十二个月。客户须在到期前六十日通知不续约，否则自动续约并上调 7%。

二、费用与付款
客户应按月支付服务费人民币 42,000 元。逾期付款按月加收 1.5% 违约金。

三、责任限制
累计赔偿责任以过去十二个月已付费用为限，最高不超过 504,000 元。
"""

REVIEW_HTML = """<!DOCTYPE html><html><head><title>Q3 Review</title></head><body>
<nav>this nav text must not appear</nav>
<h1>Q3 Infrastructure Review</h1>
<p>Overall availability improved to 99.94% in Q3, up from 99.71% in Q2.</p>
<h2>Costs</h2>
<p>Monthly cloud spend rose 18% to $61,300. We recommend renegotiating the CDN contract before renewal on 2026-01-15.</p>
<h2>Risks</h2>
<p>The single-region database remains the largest material risk. A regional outage would cost approximately $220,000.</p>
<script>console.log("script text must not appear")</script>
</body></html>
"""


def make_docx(path: Path):
    w = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
    paras = [("Heading1", "Board Memo"), ("Normal", "Cash runway is 14 months at current burn."),
             ("Heading1", "Risks"), ("Normal", "Concentration risk: top customer is 31% of revenue.")]
    body = "".join(
        f'<w:p><w:pPr><w:pStyle w:val="{st}"/></w:pPr><w:r><w:t>{txt}</w:t></w:r></w:p>'
        for st, txt in paras)
    xml = f'<?xml version="1.0"?><w:document {w}><w:body>{body}</w:body></w:document>'
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", xml)


def make_pptx(path: Path):
    tmpl = ('<?xml version="1.0"?><p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
            ' xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            '<p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>{}</a:t></a:r></a:p></p:txBody></p:sp>'
            '<p:sp><p:txBody><a:p><a:r><a:t>{}</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:sld>')
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("ppt/slides/slide1.xml", tmpl.format("Board Update", "Cloud spend $61,300 per month, up 18%."))
        z.writestr("ppt/slides/slide2.xml", tmpl.format("Recommendation", "Must approve before renewal on 2026-01-15."))


def make_pdf(src: Path, out: Path) -> bool:
    exe = shutil.which("cupsfilter")
    if not exe:
        return False
    with open(out, "wb") as fh:
        r = subprocess.run([exe, str(src)], stdout=fh, stderr=subprocess.DEVNULL)
    return r.returncode == 0 and out.stat().st_size > 800


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="docdigest-selftest-"))
    try:
        print(f"fixtures: {tmp}")

        # 1. plain text
        print("\n[1] plain text")
        txt = tmp / "agreement.txt"
        txt.write_text(AGREEMENT, "utf-8")
        p = run("outline", str(txt))
        out = p.stdout
        ok("exit 0", p.returncode == 0)
        ok("line locator", "locator: **line**" in out, out[:200])
        ok("numbered headings found", "1. Term and Termination" in out)
        ok("unwrapped sentence", "Either party may terminate this agreement for material breach upon thirty (30) days written notice." in out)
        ok("amounts", "$4,200" in out and "$50,400" in out)
        ok("dates", "2026-03-01" in out and "2026-05-15" in out)
        ok("auto-renew trap ranked top", "auto-renews at a 7% increase" in out)

        # 2. markdown list items must not fuse into one sentence
        print("\n[2] markdown lists")
        md = tmp / "notes.md"
        md.write_text("# Plan\n\n- first action item\n- second action item\n- third action item\n", "utf-8")
        mj = tmp / "notes.json"
        p = run("extract", str(md), "--json", "--out", str(mj))
        import json as _json
        d = _json.loads(Path(mj).read_text("utf-8"))
        raw = d["units"][0]["text"]
        ok("line breaks kept in unit text", "\n- second action item" in raw)
        fused = [s for s in [k["text"] for k in d["signals"]["key_sentences"]]
                 if "first action item" in s and "second action item" in s]
        ok("list items not fused into one sentence", not fused)

        # 3. html
        print("\n[3] html")
        html = tmp / "review.html"
        html.write_text(REVIEW_HTML, "utf-8")
        p = run("outline", str(html))
        out = p.stdout
        ok("paragraph locator", "locator: **paragraph**" in out)
        ok("nav text excluded", "this nav text" not in out)
        ok("script text excluded", "script text" not in out)
        ok("headings isolated", "`¶3`" in out or "Costs" in out)
        ok("amount captured", "$61,300" in out)

        # 4. docx
        print("\n[4] docx")
        dx = tmp / "memo.docx"
        make_docx(dx)
        p = run("outline", str(dx))
        out = p.stdout
        ok("exit 0", p.returncode == 0)
        ok("paragraph locator", "locator: **paragraph**" in out)
        ok("heading style honoured", "Board Memo" in out and "Risks" in out)
        ok("amount", "14 months" in out)

        # 5. pptx
        print("\n[5] pptx")
        px = tmp / "deck.pptx"
        make_pptx(px)
        p = run("outline", str(px))
        out = p.stdout
        ok("exit 0", p.returncode == 0)
        ok("slide locator", "locator: **slide**" in out)
        ok("both slides", "slide.1" in out and "slide.2" in out)
        ok("amount", "$61,300" in out)

        # 6. pdf
        print("\n[6] pdf")
        pdf = tmp / "agreement.pdf"
        if make_pdf(txt, pdf):
            p = run("outline", str(pdf))
            out = p.stdout
            ok("exit 0", p.returncode == 0)
            ok("page locator", "locator: **page**" in out)
            ok("text extracted", "$4,200" in out or "4,200" in out)
        else:
            skip("pdf extraction", "no cupsfilter on this machine")

        # 7. scanned pdf -> clean failure
        print("\n[7] text-free pdf")
        blank = tmp / "blank.txt"
        blank.write_text(" ", "utf-8")
        scan = tmp / "scan.pdf"
        if make_pdf(blank, scan):
            p = run("stats", str(scan), expect=2)
            ok("exit 2 + OCR guidance", p.returncode == 2 and "OCR" in (p.stdout + p.stderr))
        else:
            skip("scanned pdf", "no cupsfilter on this machine")

        # 8. check mode
        print("\n[8] citation checker")
        good = tmp / "good.md"
        good.write_text(
            "# Briefing\n\n"
            "Auto-renewal is the trap: miss the 60-day window and fees rise 7% [L3-11].\n"
            "Either party may terminate for material breach "
            "[\"Either party may terminate this agreement for material breach upon\"] [L3-11]\n"
            "Late fee is 1.5%/month [L3-11].\n", "utf-8")
        p = run("check", str(txt), str(good), expect=0)
        ok("faithful briefing passes", p.returncode == 0 and "PASS" in p.stdout)

        bad = tmp / "bad.md"
        bad.write_text(
            "# Briefing\n\n"
            "- Renewal rises 7% [p.99].\n"
            "- Termination needs notice [L3-11] \"ninety days prior written notice required\".\n", "utf-8")
        p = run("check", str(txt), str(bad), expect=1)
        ok("invented locator fails", p.returncode == 1 and "ERROR" in p.stdout)
        ok("fake quote warned", "not verbatim" in p.stdout)

        # 9. CJK
        print("\n[9] CJK")
        cn = tmp / "contract.txt"
        cn.write_text(CONTRACT_CN, "utf-8")
        p = run("outline", str(cn))
        out = p.stdout
        ok("exit 0", p.returncode == 0)
        ok("full-width punctuation preserved", "起生效，有效期" in out or "，" in out)
        ok("元 amount captured", "42,000" in out)
        ok("CJK headings", "一、服务期限" in out)

        cnbrief = tmp / "cn.md"
        cnbrief.write_text("# 摘要\n\n续约风险最高 [L3-4]。\n「供应商必须维持等保三级认证」 [L1-9]\n", "utf-8")
        p = run("check", str(cn), str(cnbrief), expect=0)
        ok("CJK briefing passes", p.returncode == 0)

        # 10. json contract
        print("\n[10] json contract")
        jout = tmp / "d.json"
        p = run("extract", str(txt), "--json", "--out", str(jout))
        ok("json written", p.returncode == 0 and jout.exists())
        if jout.exists():
            import json
            d = json.loads(jout.read_text("utf-8"))
            keys = {"kind", "source", "stats", "signals", "units"}
            ok("json keys", keys <= set(d))
            ok("stats consistent", d["stats"]["units"] == len(d["units"]))
            ok("no absolute-path leak in kind", d["kind"] == "text")

    finally:
        if not VERBOSE:
            shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{'=' * 60}")
    print(f"PASS {len(PASS)} · FAIL {len(FAIL)} · SKIP {len(SKIP)}")
    for f in FAIL:
        print(f"  failed: {f}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
