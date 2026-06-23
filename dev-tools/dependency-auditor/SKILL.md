---
name: dependency-auditor
description: "Use when auditing project dependencies — checks for outdated packages, security vulnerabilities, stale lockfiles, unused deps, and generates safe batch update plans for npm, pip, cargo, go, gem, and maven ecosystems."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [dependencies, npm, pip, cargo, go, maven, security, updates, lockfile, dev-tools]
    related_skills: [project-scaffolder, env-setup-debugger, code-review-helper]
---

# Dependency Auditor / 依赖审计工具

> Scan projects for outdated, insecure, or cruft dependencies — then generate a safe, reviewable update plan. Supports npm, pip, cargo, go mod, bundler, and maven ecosystems.

---

## Overview

Dependency rot is a silent productivity killer. This skill systematically audits a project's dependency graph, separates safe updates from risky ones, detects security advisories, and produces an actionable update plan — all without breaking your build.

| Feature | What it does | Supported ecosystems |
|---------|-------------|---------------------|
| **Outdated check** | Lists all deps with semver-compatible & latest versions | npm, pip, cargo, go, gem, maven |
| **Security audit** | Runs ecosystem-specific vuln scanners | npm audit, pip-audit, cargo audit, govulncheck, bundle audit, mvn owasp |
| **Lockfile health** | Detects stale/absent lockfiles, mismatched hashes | package-lock, yarn.lock, pnpm-lock, poetry.lock, go.sum, Gemfile.lock |
| **Unused deps** | Finds packages imported nowhere in source | depcheck (npm), pip-check, cargo-udeps, go mod why |
| **Update plan** | Classifies updates into safe / minor / breaking | All ecosystems |
| **Batch execution** | Applies safe updates, runs tests, reports results | All ecosystems |

---

## When to Use

Trigger this skill when:

- You join a project and want to assess dependency health
- `npm outdated` / `pip list --outdated` reveals many packages
- A Dependabot or Renovate PR is blocked by conflicts
- You're preparing a release and want to clean up deps
- CI is failing due to security advisories
- A `lockfile` is missing or out of sync with manifest
- You want to remove unused packages before a refactor
- You haven't run `npm audit` or equivalent in weeks

---

## Core Workflow

### Step 1: Detect project ecosystem

Identify the project's package manager(s) by checking for manifest files:

```
Detect order:
1. package.json       → npm / yarn / pnpm
2. pyproject.toml      → pip / poetry / pdm
3. requirements.txt    → pip
4. Cargo.toml          → cargo
5. go.mod              → go
6. Gemfile             → bundler
7. pom.xml             → maven
```

Run from project root:

```bash
# Quick ecosystem check
ls package.json pyproject.toml Cargo.toml go.mod Gemfile pom.xml requirements.txt 2>/dev/null
```

If multiple manifests exist, audit each ecosystem separately in order.

### Step 2: Run outdated & security checks

For each detected ecosystem, run the appropriate tools:

**npm / yarn / pnpm:**

```bash
# Outdated packages (semver-compatible + latest)
npm outdated --json 2>/dev/null | jq '.[] | {name, current, wanted, latest}'

# Security audit
npm audit --json 2>/dev/null | jq '{metadata: .metadata, vulnerabilities: [.vulnerabilities | to_entries[] | {key, severity: .value.severity, via: .value.via, range: .value.range}]}' 2>/dev/null

# Lockfile health
test -f package-lock.json && echo "lockfile OK: $(wc -l < package-lock.json) lines" || echo "WARN: no lockfile"
node -e "try{require('package-lock.json');console.log('LOCKFILE: valid')}catch(e){console.log('LOCKFILE: invalid')}" 2>/dev/null

# Unused deps (requires install: npx depcheck)
npx depcheck --json 2>/dev/null | jq '{unused: .dependencies, missing: .missing}'
```

**pip / poetry:**

```bash
# Outdated
pip list --outdated --format=json 2>/dev/null | jq '.[] | {name, version, latest_version}'

# Security (requires: pip install pip-audit)
pip-audit --format=json 2>/dev/null | jq '.'

# Lockfile health (poetry)
test -f poetry.lock && echo "lockfile present" || echo "WARN: no poetry.lock"
pip freeze 2>/dev/null | head -5

# Unused (requires: pip install pip-check)
pip-check 2>/dev/null
```

**cargo:**

```bash
# Outdated (requires: cargo install cargo-outdated)
cargo outdated --format=json 2>/dev/null

# Security (requires: cargo install cargo-audit)
cargo audit --json 2>/dev/null

# Lockfile health
test -f Cargo.lock && echo "lockfile OK" || echo "WARN: no Cargo.lock"

# Unused (requires: cargo install cargo-udeps)
cargo +nightly udeps 2>/dev/null
```

**go mod:**

```bash
# Outdated (requires: go get golang.org/x/tools/cmd/goimports)
go list -u -m all 2>/dev/null | grep '\['

# Security (requires: go install golang.org/x/vuln/cmd/govulncheck@latest)
govulncheck ./... 2>/dev/null

# Lockfile health
test -f go.sum && echo "go.sum present ($(wc -l < go.sum) entries)" || echo "WARN: no go.sum"
go mod verify 2>&1

# Unused
go mod tidy -v 2>&1 | grep -v 'unused'
```

**bundler (gem):**

```bash
# Outdated
bundle outdated --json 2>/dev/null

# Security
bundle audit --format json 2>/dev/null

# Lockfile health
test -f Gemfile.lock && echo "lockfile present" || echo "WARN: no Gemfile.lock"
```

**maven:**

```bash
# Outdated (requires: mvn versions:display-dependency-updates)
mvn versions:display-dependency-updates -q 2>/dev/null

# Security (requires: mvn org.owasp:dependency-check-maven:check)
mvn org.owasp:dependency-check-maven:aggregate -q 2>/dev/null
```

### Step 3: Build the update plan

Classify each outdated dependency:

| Category | Criteria | Action |
|----------|----------|--------|
| **🔒 Safe** | Patch version bump only (x.y.z → x.y.z+1) | Auto-update |
| **✅ Minor** | Minor version bump (x.y → x.y+1), no semver-breaking changes known | Update + run tests |
| **⚠️ Review** | Major version bump (x → x+1) or security advisory | Manual review required |
| **❌ Breaking** | Known breaking changes in changelog, or deprecation | Skip, plan migration |

Generate the plan as structured output:

```
## Dependency Update Plan — {project-name}

### Safe (auto-update, {N} packages)
- {pkg1}: {current} → {latest}
- {pkg2}: {current} → {latest}

### Minor (test after update, {N} packages)
- {pkg3}: {current} → {latest}

### Needs Review (breaking changes, {N} packages)
- {pkg4}: {current} → {latest}
  - Breaking changes: {summary}
  - Recommendation: {action}

### Security Alerts ({N} critical, {N} high)
- {pkg5}: {CVE} ({severity}) — {summary}
  - Fix version: {fixedIn}

### Unused Dependencies ({N})
- {pkg6}: last used in {file}
  - Action: `npm uninstall {pkg6}`
```

### Step 4: Apply safe updates

For **Safe** and **Minor** categories, apply updates:

```bash
# npm — update all safe/minor
npm update

# or update specific packages
npm install {pkg}@latest

# pip — update specific
pip install --upgrade {pkg}

# poetry
poetry update {pkg}

# cargo
cargo update -p {pkg}

# go
go get {pkg}@latest

# bundler
bundle update {pkg}
```

After each batch, run the project's test suite:

```bash
npm test || pytest || cargo test || go test ./... || bundle exec rspec
```

If tests fail, roll back the failing package:

```bash
# npm — revert
npm install {pkg}@{current_version}

# pip
pip install {pkg}=={current_version}

# git-based rollback
git checkout -- package.json package-lock.json
npm install
```

### Step 5: Fix lockfile issues

Common lockfile problems and fixes:

```bash
# Regenerate lockfile from manifest
# npm
rm package-lock.json && npm install

# pip (poetry)
poetry lock

# cargo
cargo generate-lockfile

# go
go mod tidy

# bundler
bundle lock --update
```

### Step 6: Generate report

Summarize the audit:

```markdown
# Dependency Audit Report — {date}

**Project:** {path}
**Ecosystem:** {npm/pip/cargo/go/gem/maven}

## Summary
| Metric | Count |
|--------|-------|
| Total dependencies | {N} |
| Up-to-date | {N} |
| Safe to update | {N} |
| Needs review | {N} |
| Security advisories | {N (C:H:M:L)} |
| Unused | {N} |

## What was updated
- {pkg1}: {current} → {new} (✓ tests passed)
- {pkg2}: {current} → {new} (✓ tests passed)

## Remaining work
- Review {N} major version bumps
- Address {N} security advisories
- Remove {N} unused packages

## Next audit
- Run weekly on active projects
- Integrate into CI with `npm audit --audit-level=high`
```

---

## Example Invocations

### Example 1: Full audit on a Node.js project

**User:** "Audit the dependencies in my project and fix what's safe"

**Agent action:**
1. Checks `package.json` exists → detects npm ecosystem
2. Runs `npm outdated --json`, `npm audit --json`, `npx depcheck --json`
3. Builds update plan:
   - Safe: `lodash` 4.17.20 → 4.17.21, `express` 4.18.1 → 4.18.2
   - Minor: `typescript` 5.0.4 → 5.1.6
   - Review: `webpack` 4 → 5 (breaking)
   - Security: `axios` 0.21.1 → 0.28.0 (CVE-2023-45857, HIGH)
4. Runs `npm update`, then `npm test` — passes
5. Reports:
   ```
   ✅ Updated 3 packages (lodash, express, typescript)
   ✅ Tests pass
   ⚠️ Skipped: webpack (major bump — needs manual review)
   🔴 CVE-2023-45857 in axios — upgrade to 0.28.0 required
   ```

### Example 2: Python project health check

**User:** "Check if my Python project's deps are safe"

**Agent action:**
1. Detects `pyproject.toml` + `requirements.txt`
2. Runs `pip list --outdated --format=json`, `pip-audit --format=json`
3. Finds `requests` 2.28.0 → 2.31.0 (fixes CVE-2023-32681)
4. Applies: `pip install --upgrade requests`
5. Runs `pytest` — all 47 tests pass
6. Reports: "All dependencies up to date. 1 security fix applied (requests)."

### Example 3: Go module lockfile corruption

**User:** "go.sum is out of sync, fix it for me"

**Agent action:**
1. Runs `go mod verify` → sees hash mismatch
2. Runs `go mod tidy` to regenerate
3. Verifies: `go mod verify` → "all modules verified"
4. Runs `go test ./...` → passes
5. Reports: "go.sum regenerated and verified. All tests pass."

---

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| `npm audit` fails with "no audit available" | Run `npm install` first to populate node_modules, or use `npm audit --omit=dev` |
| `cargo audit` not installed | `cargo install cargo-audit` — requires Rust toolchain |
| `pip-audit` not installed | `pip install pip-audit` — may need `--break-system-packages` on modern Linux |
| Lockfile conflict during update | If git-tracked: `git checkout -- package-lock.json && npm install` to restart |
| Major version bump has no changelog | Check GitHub releases page or commit history between versions |
| Test suite doesn't exist | Use `npm run build` or `make build` as minimal smoke test |
| Monorepo with multiple packages | Run audit from each workspace root. Use `--workspaces` flag for npm workspaces |
| Private registry packages | Set `NPM_CONFIG_REGISTRY` / `PIP_INDEX_URL` / `CARGO_REGISTRIES_*` env vars |
| `go mod verify` fails but `go mod tidy` doesn't fix it | Delete go.sum and re-run `go mod tidy`, then `go mod verify` |
| `govulncheck` reports false positives | Check the CVE details — some affect only specific OS/arch or indirect usage paths |

---

## Verification Checklist

- [ ] Project ecosystem detected correctly (manifest file found)
- [ ] `outdated` check ran without errors
- [ ] Security audit ran (or fallback message if tool missing)
- [ ] Lockfile validated — present and internally consistent
- [ ] Unused dependencies identified (with tool if available)
- [ ] Update plan built with correct severity classification
- [ ] Safe updates applied
- [ ] Test suite executed after updates
- [ ] Failed updates rolled back gracefully
- [ ] Report generated with summary and remaining action items
- [ ] If lockfile was corrupted: verified with `npm ci` / `poetry install` / equivalent clean install

---

## Data Sources & Accuracy

- **Version freshness**: Queried from public registries (npmjs.org, PyPI, crates.io, pkg.go.dev, rubygems.org, Maven Central) via built-in CLI tools (`npm outdated`, `pip list --outdated`, `cargo outdated`, `go list -u`, `bundle outdated`, `mvn versions:display-dependency-updates`). Accuracy depends on the registry being reachable and the package metadata being up to date.
- **Security advisories**: Uses ecosystem-specific databases — npm advisory database, PyPA advisory database (via pip-audit), RustSec (via cargo-audit), Go vulnerability database (via govulncheck), Ruby Advisory DB (via bundle-audit), OWASP Dependency-Check (NVD + retired). False positives are possible; always verify CVE details before acting.
- **Breaking change detection**: Based on semver analysis (major version bump) and heuristic scanning of CHANGELOG / release notes where available. Not perfect — always run tests before deploying.
- **Unused dependency detection**: Heuristic (import scanning). May report false positives for packages used dynamically (plugins, CLI tools, build-time only).
- **Lockfile integrity**: Verified against manifest files using ecosystem-native commands (`npm ci --dry-run`, `go mod verify`, `poetry lock --check`). Cannot detect subtle hash collisions.
