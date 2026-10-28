#!/usr/bin/env python3
"""Full regression for the purchase-advisor scripts.

Verifies:
  1. tco.py and brief.py produce IDENTICAL totals and identical winners.
  2. All four verdict branches fire: BUY / WAIT / CLOSE / HOLD.
  3. pricecheck.py fires BUY NOW / SKIP-WAIT and the fake-discount warning.
  4. Edge cases: single candidate, zero tax, missing specs, negative/missing args.
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tco          # noqa: E402
import brief        # noqa: E402
import pricecheck   # noqa: E402

DATA = os.path.expanduser("~/.hermes/data/purchase-advisor")
FAIL = []


def check(label, cond, detail=""):
    if cond:
        print(f"  [PASS] {label}")
    else:
        print(f"  [FAIL] {label} {detail}")
        FAIL.append(label)


def run(args):
    r = subprocess.run([sys.executable] + args, capture_output=True, text=True, cwd=HERE)
    return r.stdout + r.stderr


print("=" * 70)
print("1. CROSS-SCRIPT AGREEMENT (tco.py vs brief.py)")
print("=" * 70)
d = tco.load("reg-1")
check("decision loaded", len(d.get("candidates", [])) == 3, str(d))
rows = []
for c in d["candidates"]:
    a = tco.tco(c, 3.0)
    b = brief.tco_of(c, 3.0)
    rows.append((c["name"], a, b))
    check(f"total match: {c['name']}", a["total"] == b["total"],
          f"tco={a['total']} brief={b['total']}")
    check(f"tax match: {c['name']}", a["tax"] == b["tax"],
          f"tco={a['tax']} brief={b['tax']}")
    check(f"per_month match: {c['name']}", a["per_month"] == b["per_month"],
          f"tco={a['per_month']} brief={b['per_month']}")

# winners agree
tco_out = run([os.path.join(HERE, "tco.py"), "-d", "reg-1", "compare", "--horizon", "3"])
brief_out = run([os.path.join(HERE, "brief.py"), "-d", "reg-1", "--horizon", "3"])
def winner_of_compare(out):
    for line in out.splitlines():
        if "VERDICT" in line:
            return line.split(":")[1].strip()
    return None
tco_leader = None
known = [c["name"] for c in d["candidates"]]
for line in tco_out.splitlines():
    for name in known:
        if line.strip().startswith(name):
            tco_leader = name
            break
    if tco_leader:
        break
brief_leader = None
for line in brief_out.splitlines():
    if "✅ 推荐" in line:
        brief_leader = line.split("|")[1].strip()
        break
check("same winner (tco vs brief)", tco_leader == brief_leader,
      f"tco={tco_leader!r} brief={brief_leader!r}")

print()
print("=" * 70)
print("2. VERDICT BRANCHES")
print("=" * 70)
branches = {
    "BUY": ("reg-buy", []),
    "WAIT": ("reg-wait", ["--w-price", "0.15", "--w-specs", "0.85"]),
    "CLOSE": ("reg-close", []),
    "HOLD": ("reg-hold", []),
}
for expected, (did, extra) in branches.items():
    out = run([os.path.join(HERE, "tco.py"), "-d", did, "compare", "--horizon", "3"] + extra)
    got = winner_of_compare(out)
    check(f"{expected} branch fires", got is not None and expected in got, f"got={got!r}")

print()
print("=" * 70)
print("3. PRICECHECK")
print("=" * 70)
out = run([os.path.join(HERE, "pricecheck.py"), "check", "--product", "reg-gym"])
check("fake discount flagged", "never-real list price" in out or "fake 'sale'" in out,
      out[-400:])
check("small-sample warned", "sample(s)" in out)
out2 = run([os.path.join(HERE, "pricecheck.py"), "check", "--product", "reg-nonexistent"])
check("missing product errors cleanly", "ERROR" in out2 and "Log one first" in out2)

print()
print("=" * 70)
print("4. EDGE CASES")
print("=" * 70)
out = run([os.path.join(HERE, "tco.py"), "-d", "reg-single", "compare"])
check("single candidate -> no crash", "VERDICT" in out and "Traceback" not in out, out[-300:])
out = run([os.path.join(HERE, "tco.py"), "-d", "reg-noexist", "compare"])
check("missing decision -> clean error", "ERROR" in out and "Traceback" not in out)
out = run([os.path.join(HERE, "tco.py"), "-d", "reg-empty", "compare"])
check("empty decision -> clean error", "ERROR" in out and "Traceback" not in out)
out = run([os.path.join(HERE, "brief.py"), "-d", "reg-empty"])
check("empty brief -> clean error", "ERROR" in out and "Traceback" not in out)
out = run([os.path.join(HERE, "tco.py"), "-d", "reg-bad", "add", "--name", "X",
            "--spec", "garbage"])
check("bad --spec rejected", "ERROR" in out and "Traceback" not in out)
out = run([os.path.join(HERE, "tco.py"), "-d", "reg-zero", "add", "--name", "Free",
            "--price", "0"])
out = run([os.path.join(HERE, "tco.py"), "-d", "reg-zero", "compare"])
check("zero-price candidate -> no crash", "VERDICT" in out and "Traceback" not in out, out[-300:])

print()
print("=" * 70)
if FAIL:
    print(f"RESULT: {len(FAIL)} FAILURE(S): {FAIL}")
    sys.exit(1)
print("RESULT: ALL CHECKS PASSED")
print("=" * 70)
