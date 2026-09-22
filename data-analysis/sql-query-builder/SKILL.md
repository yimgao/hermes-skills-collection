---
name: sql-query-builder
description: "Turn plain-English questions into dialect-aware SQL — Postgres, MySQL, SQLite, BigQuery, Snowflake, Redshift. Generates schema-aware queries with EXPLAIN plans, parameter binding, performance hints. Pairs with csv-explorer, json-explorer, time-series-analyzer, api-contract-tester."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [sql, postgres, mysql, sqlite, bigquery, snowflake, redshift, query-builder, database, analytics, schema, data-analysis, dev-tools]
    related_skills: [csv-explorer, json-explorer, time-series-analyzer, api-contract-tester, regex-builder, schema-explorer]
---

# SQL Query Builder / SQL 查询生成器

> From *"find me the top 10 customers by revenue last quarter, excluding refunds"* to a tested, schema-validated SQL query in 30 seconds — dialect-aware (Postgres / MySQL / SQLite / BigQuery / Snowflake / Redshift), with parameter binding, EXPLAIN plan hints, and copy-pasteable snippets for ORM / psql / the BigQuery console.

Every analyst, PM, backend dev, and data engineer types SQL every day. But most "write a query" requests in chat produce:

- ❌ Wrong dialect syntax (`LIMIT 10` vs `TOP 10` vs `FETCH FIRST 10 ROWS ONLY`)
- ❌ Hallucinated table / column names because the model never read the schema
- ❌ SQL injection bait — string-concatenated user input
- ❌ Date arithmetic that breaks across timezones
- ❌ N+1 patterns that look fine in dev and die in prod

**SQL Query Builder** fixes all of these. It reads your schema (DDL, `information_schema`, or a sample query result), confirms the intent in 1–2 quick questions, and returns production-grade SQL with the `?` / `$1` / `@param` placeholders already wired.

## Overview

| Capability | Input | Output |
|------------|-------|--------|
| **Natural Language → SQL** | *"users who upgraded in the last 30 days and have >$1k MRR"* | Dialect-correct SELECT with joins, filters, params |
| **Schema-aware Generation** | Table DDL / `information_schema` dump / sample rows | Validates table & column names before generating |
| **Dialect Translation** | A query you wrote for Postgres | Equivalent in MySQL / SQLite / BigQuery / Snowflake / Redshift |
| **Parameter Binding** | Any user-controlled values | `:param` / `?` / `@var` placeholders, never string concat |
| **EXPLAIN Plan Hints** | A generated query | Cost, seq scan warnings, missing-index candidates |
| **Query Optimization** | A slow query | Index suggestions, rewrite patterns (CTE vs subquery, EXISTS vs IN) |
| **Migration Generator** | *"rename column `old_name` to `new_name`"* | Dialect-correct `ALTER TABLE` with rollback |
| **Pattern Library** | Common use case | 25+ battle-tested recipes (window fns, dedup, cohort, funnel) |
| **ORM Conversion** | Generated SQL | Equivalent Prisma / SQLAlchemy / Knex / Drizzle snippet |
| **Dry-run Validator** | SQL + target DB URL | Local EXPLAIN / parse-only via `EXPLAIN` (no execution) |

## When to Use

- *"Find me all users who signed up last week and haven't logged in since"*
- *"Top 10 products by revenue, broken down by region, excluding refunds"*
- *"Count orders per customer, including those with zero orders"*
- *"Write a Postgres query for a rolling 7-day average of daily active users"*
- *"Translate this MySQL query to BigQuery Standard SQL"*
- *"I have a slow query — how do I speed it up?"*
- *"Write the ALTER TABLE to rename `user_id` to `account_id` across Postgres + Redshift"*
- *"Generate the Prisma / SQLAlchemy / Knex version of this query"*
- *"Find duplicate rows in `events` where (user_id, event_type, day) should be unique"*
- *"Compute month-over-month retention for cohort 2025-Q1"*
- *"Convert this CSV / JSON sample into a CREATE TABLE statement"*
- *"What's the difference between `RANK()` and `DENSE_RANK()` for this use case?"*
- *"帮我写一条 SQL，找最近 30 天复购的上海用户"*
- *"查询连续 7 天都登录的用户，MySQL 8.0"*
- *"Postgres 怎么写递归 CTE 计算组织架构？"*

### Trigger Phrases

| Phrase (EN) | Phrase (中文) |
|-------------|---------------|
| "write a SQL query" | "帮我写一条 SQL" |
| "generate SQL for" | "查询 … 的 SQL" |
| "translate this to MySQL/Postgres/BigQuery" | "翻译成 MySQL / Postgres / BigQuery" |
| "find users/orders/events where…" | "找出 … 的用户/订单/事件" |
| "top N by …" | "按 … 排前 N" |
| "explain / optimize this query" | "这条 SQL 怎么优化" |
| "write the migration for…" | "生成迁移 SQL" |

---

## Core Workflow

### Step 1: Confirm the Three Inputs

Before writing any SQL, lock down three things. If the user is missing any of them, ask in **one** tight message — not five.

```text
1. INTENT     — what does "success" look like? (rows, columns, sort, limit)
2. SCHEMA     — table(s) + relevant columns. Source:
                • Paste CREATE TABLE / DDL
                • Paste \d+ output from psql
                • Paste a sample row (CSV / JSON)
                • Point at a connection string (we read information_schema only, never data)
3. DIALECT    — Postgres / MySQL / SQLite / BigQuery / Snowflake / Redshift / SQL Server
```

**The four-question test** (skip if user already gave specifics):

| Question | Why it matters |
|----------|----------------|
| Aggregate or row-level? | `GROUP BY` vs flat `SELECT` — different shape |
| Time window? Hard-coded or relative? | `'2025-01-01'` vs `NOW() - INTERVAL '30 days'` — debugging & caching differ |
| Include NULLs? | `WHERE x > 0` excludes NULLs silently — use `x > 0 OR x IS NULL` |
| Need dedup / latest-per-group? | Triggers window functions (`ROW_NUMBER`, `DISTINCT ON`, `QUALIFY`) |

### Step 2: Validate the Schema

Never trust a hallucinated column name. If the user pasted DDL or a sample row, parse it. Otherwise, ask for:

- For Postgres / Redshift: `\d+ schema.table` or `SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '...'`
- For MySQL: `SHOW CREATE TABLE users;` or `DESCRIBE users;`
- For BigQuery / Snowflake: `INFORMATION_SCHEMA.COLUMNS` query
- For SQLite: `PRAGMA table_info(users);` or `.schema users`

```python
# Minimal schema parser — works for CREATE TABLE dumps
import re

def parse_create_table(ddl: str) -> dict:
    """Parse a CREATE TABLE statement into {table: [cols]}."""
    m = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["`[]?(\w+)["`]]?\s*\((.*?)\)\s*(?:ENGINE|CHARSET|COLLATE|;|$)',
                  ddl, re.DOTALL | re.IGNORECASE)
    if not m:
        return {}
    table, body = m.group(1), m.group(2)
    cols = []
    for line in body.split(','):
        line = line.strip().rstrip(',').strip()
        if not line or line.upper().startswith(('PRIMARY', 'FOREIGN', 'UNIQUE', 'KEY', 'INDEX', 'CONSTRAINT', 'CHECK')):
            continue
        parts = line.split(None, 2)
        if len(parts) >= 2:
            cols.append({"name": parts[0].strip('"[]`'), "type": parts[1].upper()})
    return {table: cols}
```

### Step 3: Generate the Query (Dialect-Aware)

Pick the right **placeholder syntax** and **date / limit / string functions** for the dialect. Always parameterize user input — never `f"WHERE name = '{name}'"`.

#### 3a. Placeholder Reference

| Dialect | Placeholder | Example |
|---------|-------------|---------|
| Postgres / SQLite | `$1, $2, …` or `?` | `WHERE id = $1` |
| MySQL | `?` | `WHERE id = ?` |
| BigQuery | `@paramName` | `WHERE id = @user_id` |
| Snowflake | `?` or `:name` (bind) | `WHERE id = ?` |
| Redshift | `?` | `WHERE id = ?` |
| SQL Server | `@param` | `WHERE id = @user_id` |

#### 3b. Common Query Patterns

```sql
-- 1) Latest record per group (dedup) ─────────────────────────────────
-- Postgres: DISTINCT ON
SELECT DISTINCT ON (customer_id) customer_id, created_at, amount
FROM orders
ORDER BY customer_id, created_at DESC;

-- BigQuery / Snowflake: QUALIFY + ROW_NUMBER
SELECT customer_id, created_at, amount
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at DESC) rn
  FROM orders
) t
WHERE rn = 1;

-- MySQL: window fn + subquery
SELECT customer_id, created_at, amount FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at DESC) rn
  FROM orders
) t WHERE rn = 1;

-- 2) Top-N per group ───────────────────────────────────────────────
-- Postgres / BigQuery / Snowflake
SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY region ORDER BY revenue DESC) rk
  FROM sales_summary
) t WHERE rk <= 10;

-- MySQL 8+ / Postgres (alternative using LATERAL)
-- 3) Cohort retention (month-0 active, +N month still active) ───────
WITH cohort AS (
  SELECT user_id, DATE_TRUNC('month', signup_at) cohort_month
  FROM users
),
activity AS (
  SELECT user_id, DATE_TRUNC('month', event_at) active_month
  FROM events
)
SELECT c.cohort_month,
       a.active_month,
       COUNT(DISTINCT c.user_id) AS retained_users
FROM cohort c
JOIN activity a ON c.user_id = a.user_id
   AND a.active_month BETWEEN c.cohort_month
                          AND c.cohort_month + INTERVAL '6 months'
GROUP BY 1, 2
ORDER BY 1, 2;

-- 4) Rolling 7-day DAU ─────────────────────────────────────────────
SELECT day,
       AVG(dau) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) dau_7d_avg
FROM (
  SELECT DATE(event_at) day, COUNT(DISTINCT user_id) dau
  FROM events
  WHERE event_at >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY 1
) t;

-- 5) Find gaps in a time series ────────────────────────────────────
-- Postgres: generate_series + LEFT JOIN
SELECT gs::date AS day,
       COALESCE(e.cnt, 0) AS events
FROM generate_series(CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE, INTERVAL '1 day') gs
LEFT JOIN (
  SELECT DATE(created_at) d, COUNT(*) cnt FROM events GROUP BY 1
) e ON e.d = gs::date;
```

#### 3c. Date / String / Aggregate Function Map

| Concept | Postgres | MySQL | SQLite | BigQuery | Snowflake |
|---------|----------|-------|--------|----------|-----------|
| Now | `NOW()` | `NOW()` | `CURRENT_TIMESTAMP` | `CURRENT_TIMESTAMP()` | `CURRENT_TIMESTAMP()` |
| Date diff days | `DATE_PART('day', a - b)` | `DATEDIFF(a, b)` | `julianday(a) - julianday(b)` | `DATE_DIFF(a, b, DAY)` | `DATEDIFF(day, a, b)` |
| Last 30 days | `INTERVAL '30 days'` | `INTERVAL 30 DAY` | `DATE('now','-30 days')` | `DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)` | `DATEADD(day, -30, CURRENT_DATE)` |
| Truncate month | `DATE_TRUNC('month', d)` | `DATE_FORMAT(d, '%Y-%m-01')` | `strftime('%Y-%m-01', d)` | `DATE_TRUNC(d, MONTH)` | `DATE_TRUNC('month', d)` |
| String concat | `a \|\| b` | `CONCAT(a, b)` | `a \|\| b` | `CONCAT(a, b)` | `CONCAT(a, b)` |
| Boolean | `TRUE / FALSE` | `TRUE / FALSE` (1/0) | `1 / 0` | `TRUE / FALSE` | `TRUE / FALSE` |
| Limit syntax | `LIMIT 10` | `LIMIT 10` | `LIMIT 10` | `LIMIT 10` | `LIMIT 10` |
| Top-N idiom | `LIMIT 10` | `LIMIT 10` | `LIMIT 10` | `LIMIT 10` | `LIMIT 10` |

### Step 4: Add Performance & Safety Annotations

Every generated query gets a short annotation block:

```sql
-- [PERF]  Hits index: users(email) — verify with EXPLAIN
-- [PERF]  Sort cost: ORDER BY created_at DESC may need composite index (users, created_at DESC)
-- [SAFETY] user_email is parameterized — no injection risk
-- [NULL]  Filter `amount > 0` excludes NULL amounts — add `OR amount IS NULL` if you want them
-- [TZ]    created_at assumed UTC. If stored as local TZ, wrap in `AT TIME ZONE 'America/Los_Angeles'`
```

If the user shared a connection string, run **EXPLAIN** (not the query itself):

```python
import psycopg  # or pymysql, sqlite3, google.cloud.bigquery, snowflake-connector-python
def explain(conn, dialect: str, query: str) -> str:
    if dialect == "postgres":
        return "\n".join(str(row[0]) for row in conn.execute(f"EXPLAIN {query}").fetchall())
    if dialect == "mysql":
        rows = conn.execute(f"EXPLAIN {query}").fetchall()
        return format_mysql_explain(rows)
    if dialect == "sqlite":
        return "\n".join(str(r[0]) for r in conn.execute(f"EXPLAIN QUERY PLAN {query}").fetchall())
    if dialect in ("bigquery", "snowflake", "redshift"):
        return "Dry-run via client.query_dry_run() / session.sql(...).explain_plan()"
```

Flag the following automatically:

- ⚠️ Sequential scan on a table > 10k rows
- ⚠️ Implicit type cast (`WHERE varchar_col = 123` — Postgres will skip index)
- ⚠️ `SELECT *` from wide tables
- ⚠️ `OR` across different columns (kills index merge)
- ⚠️ Functions on indexed columns in WHERE (`WHERE DATE(created_at) = …` — use range instead)
- ⚠️ Missing `LIMIT` on user-facing queries

### Step 5: Return in Three Formats

Most users need one format, not all three. Default to **(1) raw SQL**, then offer:

```sql
-- (1) Raw SQL with parameter placeholders (Postgres)
SELECT u.id, u.email, COUNT(o.id) AS order_count, SUM(o.amount) AS ltv
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.signup_at >= NOW() - INTERVAL '90 days'
  AND u.country = $1
GROUP BY u.id, u.email
HAVING COUNT(o.id) >= $2
ORDER BY ltv DESC
LIMIT $3;
```

```python
# (2) SQLAlchemy (Python)
from sqlalchemy import text
q = text("""
SELECT u.id, u.email, COUNT(o.id) AS order_count, SUM(o.amount) AS ltv
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.signup_at >= NOW() - INTERVAL '90 days'
  AND u.country = :country
GROUP BY u.id, u.email
HAVING COUNT(o.id) >= :min_orders
ORDER BY ltv DESC
LIMIT :limit_count;
""")
result = conn.execute(q, {"country": "US", "min_orders": 3, "limit_count": 100}).fetchall()
```

```typescript
// (3) Prisma (TypeScript)
const rows = await prisma.$queryRaw`
  SELECT u.id, u.email, COUNT(o.id)::int AS order_count, SUM(o.amount)::numeric AS ltv
  FROM users u
  LEFT JOIN orders o ON o.user_id = u.id
  WHERE u.signup_at >= NOW() - INTERVAL '90 days'
    AND u.country = ${country}
  GROUP BY u.id, u.email
  HAVING COUNT(o.id) >= ${minOrders}
  ORDER BY ltv DESC
  LIMIT ${limitCount};
`;
```

```javascript
// (4) Knex.js (Node)
const rows = await knex('users as u')
  .leftJoin('orders as o', 'o.user_id', 'u.id')
  .where('u.signup_at', '>=', knex.raw("NOW() - INTERVAL '90 days'"))
  .andWhere('u.country', country)
  .select('u.id', 'u.email')
  .count('o.id as order_count')
  .sum('o.amount as ltv')
  .groupBy('u.id', 'u.email')
  .having(knex.raw('count(o.id) >= ?', [minOrders]))
  .orderBy('ltv', 'desc')
  .limit(limitCount);
```

---

## Example Invocations

### Example 1 — "Top 10 customers by LTV, last quarter, US only"

**User:**
> *Top 10 customers by lifetime value, US only, signed up in the last quarter. Postgres.*

**Agent (after one clarifying question about column naming):**

```text
I'll assume `users.signup_at`, `orders.amount`, `orders.user_id`. Generating Postgres SQL…
```

```sql
-- [PERF]  Hit indexes: users(signup_at), users(country), orders(user_id)
-- [SAFETY] country code is parameterized
SELECT u.id, u.email, SUM(o.amount)::numeric AS ltv
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE u.country = $1                    -- e.g. 'US'
  AND u.signup_at >= DATE_TRUNC('quarter', NOW())
GROUP BY u.id, u.email
ORDER BY ltv DESC
LIMIT $2;                               -- 10
```

```python
# SQLAlchemy
from sqlalchemy import text
q = text("""
SELECT u.id, u.email, SUM(o.amount)::numeric AS ltv
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE u.country = :country
  AND u.signup_at >= DATE_TRUNC('quarter', NOW())
GROUP BY u.id, u.email
ORDER BY ltv DESC
LIMIT :limit_count;
""")
rows = conn.execute(q, {"country": "US", "limit_count": 10}).fetchall()
```

**Follow-up:**
> *"Add a column for last-order date and exclude refunded orders."*

```sql
SELECT u.id, u.email,
       SUM(o.amount) FILTER (WHERE o.status != 'refunded')::numeric AS ltv,
       MAX(o.created_at) FILTER (WHERE o.status != 'refunded') AS last_order_at
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE u.country = $1
  AND u.signup_at >= DATE_TRUNC('quarter', NOW())
GROUP BY u.id, u.email
ORDER BY ltv DESC
LIMIT $2;
```

---

### Example 2 — "Translate between dialects"

**User:**
> *I have this Postgres query. Make it work on BigQuery.*

**Input:**
```sql
SELECT DISTINCT ON (customer_id) customer_id, created_at, amount
FROM orders
ORDER BY customer_id, created_at DESC;
```

**Output:**

```sql
-- BigQuery: DISTINCT ON → QUALIFY + ROW_NUMBER
SELECT customer_id, created_at, amount
FROM (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at DESC) AS rn
  FROM orders
) t
WHERE rn = 1;
```

**Snowflake variant** (same shape, QUALIFY is a Snowflake keyword):

```sql
SELECT customer_id, created_at, amount
FROM (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at DESC) AS rn
  FROM orders
) t
QUALIFY rn = 1;
```

---

### Example 3 — "Slow query, optimize it"

**User:**
> *This takes 14 seconds. There are 8M rows in `events`. Postgres 15.*
>
> ```sql
> SELECT user_id, COUNT(*) FROM events
> WHERE DATE(created_at) = '2025-01-15' AND event_type = 'click'
> GROUP BY user_id;
> ```

**Agent:**

```text
3 problems detected:
1. ⚠️ DATE(created_at) = ... disables the btree index on created_at → sequential scan
2. ⚠️ Missing index on (event_type) or composite (event_type, created_at)
3. ⚠️ No LIMIT — returns potentially millions of rows

Fix:
```

```sql
-- [FIX 1] Range instead of function-on-column
-- [FIX 2] Composite index recommendation:
--   CREATE INDEX CONCURRENTLY idx_events_type_created
--     ON events (event_type, created_at);

SELECT user_id, COUNT(*) AS clicks
FROM events
WHERE event_type = $1                                -- 'click'
  AND created_at >= TIMESTAMP '2025-01-15 00:00:00'
  AND created_at <  TIMESTAMP '2025-01-16 00:00:00'
GROUP BY user_id
ORDER BY clicks DESC
LIMIT $2;                                            -- guard against runaway
```

```text
Expected: index-only scan on idx_events_type_created, ~50ms.
Re-run EXPLAIN ANALYZE to confirm.
```

---

## Common Pitfalls

| Problem | Why it bites | Fix |
|---------|--------------|-----|
| `SELECT *` in production | Wide rows, breaks when columns added, sends megabytes | Explicit column list — always |
| `DATE(col) = '2025-01-15'` | Function on indexed column → seq scan | Range: `col >= '2025-01-15' AND col < '2025-01-16'` |
| `IN (SELECT …)` with NULLs | NULL never matches → silently drops rows | Use `NOT EXISTS` or add `NULL` handling |
| String concat for parameters | **SQL injection** — #1 vulnerability | Always parameterize: `$1`, `?`, `:name`, `@var` |
| `OFFSET 100000` for pagination | Scans 100k rows to skip them | Use keyset pagination: `WHERE id > $last_id ORDER BY id LIMIT 50` |
| Implicit type cast (`varchar = 123`) | Index ignored, all rows converted | Match types: `varchar = '123'` or cast the literal |
| `UNION` without `ALL` | Dedup cost, hides duplicates | `UNION ALL` unless dedup is intentional |
| Counting in a `LEFT JOIN` | `COUNT(*)` counts NULLs too, gives wrong totals | `COUNT(o.id)` instead of `COUNT(*)` |
| `ORDER BY` without `LIMIT` | Full sort of result set on every call | Always pair user-facing queries with `LIMIT` |
| `NOW()` vs `CURRENT_TIMESTAMP` | Same in most dialects, but `NOW()` in standard SQL returns start-of-transaction time | Use `CURRENT_TIMESTAMP()` in BigQuery / Snowflake |
| BigQuery `SELECT … WHERE _TABLE_SUFFIX BETWEEN …` | Partition pruning — **must** use `_TABLE_SUFFIX` (or `_PARTITIONDATE`) on the literal date | Wrap dates: `_TABLE_SUFFIX BETWEEN '20250101' AND '20250115'` |
| Snowflake / BigQuery case-sensitivity | Unquoted identifiers become UPPERCASE — `users.userId` will fail if your column is `userid` | Quote: `"userId"` or rename to snake_case |
| Hallucinated table/column names | Model invented a column that doesn't exist | Always validate against schema (Step 2). Don't trust the model's memory |

---

## Verification Checklist

Before returning any query:

- [ ] **Schema validated** — every table & column name confirmed against DDL / `information_schema` / sample rows
- [ ] **Dialect chosen** — and every function / operator exists in that dialect
- [ ] **User input parameterized** — no string interpolation; `:param` / `$1` / `?` / `@var` in place
- [ ] **NULL handling explicit** — `NULLS FIRST/LAST`, `IS NOT DISTINCT FROM`, or `OR x IS NULL`
- [ ] **Date filter uses range** — not `DATE(col) = …` unless column is on a functional/expression index
- [ ] **`LIMIT` present** on user-facing queries
- [ ] **Index check** — `EXPLAIN` run; flagged any seq scan on tables > 10k rows
- [ ] **Output format chosen** — raw SQL / SQLAlchemy / Prisma / Knex / Drizzle
- [ ] **Annotations added** — `[PERF]` / `[SAFETY]` / `[NULL]` / `[TZ]` comments on non-obvious lines
- [ ] **Test against sample row** — if user gave a sample, dry-run mentally and confirm row counts make sense

---

## Data Sources & Accuracy

- **Schema sources** (in order of reliability): `information_schema` / `SHOW CREATE TABLE` → user-pasted DDL → user-pasted sample row → model recall (last resort, must be flagged)
- **Dialect docs**: Postgres 15+ docs, MySQL 8.0+, SQLite 3.40+, BigQuery Standard SQL (current), Redshift (PG-derived), Snowflake current. Pin to versions when in doubt.
- **Dialect drift**: window functions landed in MySQL 8.0 (2018), SQLite 3.25 (2018), and BigQuery from day one. If the user is on MySQL 5.7 or SQLite <3.25, generated `ROW_NUMBER()` queries **will not run** — ask first.
- **No live data**: this skill reads schema only. Never run a non-`EXPLAIN` query against a real database unless the user explicitly says so.
- **No credentials storage**: connection strings you receive stay in the conversation; do not persist them to `~/.hermes/`.

---

## Related Skills

- **`csv-explorer`** — analyze the resulting rows
- **`json-explorer`** — analyze JSON outputs from a query
- **`time-series-analyzer`** — analyze time-series outputs (cohorts, retention, rolling windows)
- **`api-contract-tester`** — validate the API that exposes the query results
- **`regex-builder`** — for LIKE / regex matching inside WHERE clauses
- **`api-doc-generator`** — auto-generate docs that reference this SQL
- **`pr-description-writer`** — when the SQL change needs a migration PR
- **`schema-explorer`** *(if added)* — extract & cache DB schema locally