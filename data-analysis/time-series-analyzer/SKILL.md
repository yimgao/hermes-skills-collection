---
name: time-series-analyzer
description: "Analyze time series data from any CSV/JSON — sales logs, server metrics, sensor readings, ad spend, daily active users. Detect trends, seasonality, anomalies, change points, autocorrelation, and produce a structured analytical report. Pure Python stdlib, no pandas/numpy required."
author: yimgao
license: MIT
version: 1.0.0
metadata:
  hermes:
    tags: [data-analysis, time-series, statistics, anomaly-detection, trend, seasonality, forecasting]
    related_skills: [csv-explorer, json-explorer, website-health-monitor, ai-cost-tracker, screenshot-to-report]
---

# Time Series Analyzer / 时间序列分析器

> 把任何带时间戳的数据——日活、销售额、传感器读数、广告花费、API 调用量——变成可读的“趋势故事”：周期、突变、异常、相关性，一次讲清。

## Overview / 概述

Time Series Analyzer 接收一行格式为 `(timestamp, value[, ...])` 的时间序列（CSV/JSON/日志均可），输出五维分析报告：

| 维度 | 输出 | 典型问题 |
|---|---|---|
| **趋势 Trend** | 线性回归斜率、累计变化、移动平均曲线 | "在涨还是在跌？" |
| **季节性 Seasonality** | 日/周/月周期强度、自相关函数 | "周末有规律吗？" |
| **异常 Anomaly** | Z-score、IQR、季节性残差三类标记 | "昨天那个尖峰是异常吗？" |
| **突变 Change Point** | CUSUM 风格扫描定位断点 | "什么时候开始崩的？" |
| **预测 Forecast** | 朴素、季节朴素、简单指数平滑三选一 | "下周一大概多少？" |

所有计算用 Python 标准库 (`statistics`, `datetime`, `csv`, `json`)——不依赖 pandas/numpy，离线可用、跨平台、可审计。

## When to Use / 适用场景

- *"分析这份日活 CSV，看增长趋势和异常日。"*
- *"我的 API 调用量上周突然下跌，找出突变点。"*
- *"广告花费和销售额有相关性吗？滞后几天？"*
- *"传感器数据里那个凌晨三点的尖峰是不是异常？"*
- *"预测下个月的订阅收入。"*
- *"对比两个渠道的转化率季节性差异。"*
- *"JSON 日志里提取每分钟 QPS 并画趋势。"*
- *"我这个 GitHub star 增长曲线有没有 weekly pattern？"*

不适用于：高频金融 tick 数据（需要专门的库）、多元 VAR/状态空间模型、跨季节的多重叠加周期（建议引入 `statsmodels`）。

## Core Workflow / 核心工作流

### Step 1：加载与时序化

读取任意来源并把字符串时间戳归一化为 `datetime` 对象：

```python
import csv, json, re
from datetime import datetime, timedelta
from collections import defaultdict

COMMON_FORMATS = [
    "%Y-%m-%d",          # 2025-01-15
    "%Y-%m-%dT%H:%M:%S",  # ISO 8601
    "%Y-%m-%d %H:%M:%S",  # 2025-01-15 14:30:00
    "%Y/%m/%d",
    "%m/%d/%Y",          # US
    "%d/%m/%Y",          # EU
    "%Y-%m-%dT%H:%M:%SZ", # UTC
]

def parse_ts(s):
    s = s.strip().rstrip("Z")
    # Unix timestamp?
    if re.fullmatch(r"-?\d{10}(\.\d+)?", s):
        return datetime.fromtimestamp(float(s))
    for fmt in COMMON_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    # ISO with timezone
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None

def load_csv(path, time_col="timestamp", value_col="value"):
    series = []
    with open(path, newline='', encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = parse_ts(row[time_col])
            v = row[value_col].replace(",", "").replace("$", "").strip()
            try:
                val = float(v) if v else None
            except ValueError:
                continue
            if ts and val is not None:
                series.append((ts, val))
    series.sort(key=lambda x: x[0])
    return series

def load_json(path, time_key="ts", value_key="value"):
    with open(path) as f:
        data = json.load(f)
    series = []
    for item in (data if isinstance(data, list) else data.get("data", [])):
        ts = parse_ts(str(item[time_key]))
        try:
            val = float(item[value_key])
        except (KeyError, TypeError, ValueError):
            continue
        if ts:
            series.append((ts, val))
    series.sort(key=lambda x: x[0])
    return series
```

### Step 2：重采样到均匀间隔

非均匀时间戳会破坏后续所有计算。按数据密度选最稳的桶：

```python
def infer_bucket(series):
    """Auto-detect the dominant gap between consecutive points."""
    if len(series) < 2:
        return timedelta(days=1)
    diffs = [(series[i+1][0] - series[i][0]).total_seconds()
             for i in range(len(series)-1)]
    diffs.sort()
    # Use median to resist outliers
    median = diffs[len(diffs)//2]
    if median < 60:       return timedelta(seconds=60)
    if median < 3600:     return timedelta(minutes=5)
    if median < 86400:    return timedelta(hours=1)
    if median < 604800:   return timedelta(days=1)
    return timedelta(days=7)

def resample(series, bucket, agg="mean"):
    buckets = defaultdict(list)
    for ts, v in series:
        # Snap to bucket boundary
        if bucket == timedelta(days=1):
            key = ts.replace(hour=0, minute=0, second=0, microsecond=0)
        elif bucket == timedelta(hours=1):
            key = ts.replace(minute=0, second=0, microsecond=0)
        elif bucket == timedelta(minutes=5):
            key = ts.replace(minute=(ts.minute // 5) * 5, second=0, microsecond=0)
        else:
            key = ts
        buckets[key].append(v)
    out = []
    for k in sorted(buckets):
        vals = buckets[k]
        if agg == "sum":    v = sum(vals)
        elif agg == "max":  v = max(vals)
        elif agg == "min":  v = min(vals)
        elif agg == "count": v = len(vals)
        else:                v = sum(vals) / len(vals)
        out.append((k, v))
    return out
```

**桶选择原则**：日活/销售→`sum`；CPU/QPS→`mean`；事件计数→`count`；库存水位→`min`。

### Step 3：趋势、季节性、异常三件套

```python
import statistics

def linear_trend(series):
    """OLS slope & R² for x = 0..N-1, y = values."""
    n = len(series)
    if n < 2: return {"slope": 0, "r2": 0, "direction": "flat"}
    xs = list(range(n))
    ys = [v for _, v in series]
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    den_x = sum((x-mx)**2 for x in xs)
    den_y = sum((y-my)**2 for y in ys)
    slope = num / den_x if den_x else 0
    intercept = my - slope * mx
    r2 = (num*num) / (den_x*den_y) if den_x and den_y else 0
    return {
        "slope_per_step": round(slope, 6),
        "intercept": round(intercept, 2),
        "r_squared": round(r2, 4),
        "direction": "up" if slope > 0 else ("down" if slope < 0 else "flat"),
        "total_change_pct": round((slope * (n-1)) / my * 100, 1) if my else 0,
    }

def moving_average(series, window=7):
    out = []
    for i, (ts, v) in enumerate(series):
        start = max(0, i - window + 1)
        chunk = [w for _, w in series[start:i+1]]
        out.append((ts, round(sum(chunk)/len(chunk), 2)))
    return out

def autocorrelation(series, lag):
    """Pearson correlation between series and itself shifted by `lag`."""
    n = len(series)
    if lag >= n: return 0
    a = [v for _, v in series[:n-lag]]
    b = [v for _, v in series[lag:]]
    ma = sum(a)/len(a); mb = sum(b)/len(b)
    num = sum((x-ma)*(y-mb) for x, y in zip(a, b))
    den = (sum((x-ma)**2 for x in a) * sum((y-mb)**2 for y in b)) ** 0.5
    return round(num/den, 3) if den else 0

def detect_seasonality(series, max_lag=None):
    """Scan lags from 2..max_lag for the strongest autocorrelation peak."""
    n = len(series)
    max_lag = max_lag or min(n // 2, 60)
    candidates = [(lag, autocorrelation(series, lag))
                  for lag in range(2, max_lag + 1)]
    # 7, 30 are the usual suspects for daily data
    candidates.sort(key=lambda x: -abs(x[1]))
    top3 = candidates[:3]
    strongest = top3[0] if top3 else (None, 0)
    return {
        "strongest_lag_days": strongest[0],
        "strongest_corr": strongest[1],
        "top_3": top3,
        "is_seasonal": abs(strongest[1]) > 0.3,
    }

def detect_anomalies_zscore(series, threshold=3.0):
    vals = [v for _, v in series]
    if len(vals) < 3: return []
    mu = statistics.mean(vals)
    sd = statistics.stdev(vals)
    if sd == 0: return []
    out = []
    for ts, v in series:
        z = (v - mu) / sd
        if abs(z) > threshold:
            out.append({"timestamp": ts.isoformat(), "value": v,
                        "z_score": round(z, 2), "type": "spike" if z > 0 else "dip"})
    return out

def detect_anomalies_iqr(series):
    vals = [v for _, v in series]
    if len(vals) < 4: return []
    q1, q2, q3 = statistics.quantiles(vals, n=4)
    iqr = q3 - q1
    lo, hi = q1 - 1.5*iqr, q3 + 1.5*iqr
    out = []
    for ts, v in series:
        if v < lo or v > hi:
            out.append({"timestamp": ts.isoformat(), "value": v,
                        "bound": (round(lo,2), round(hi,2)),
                        "type": "spike" if v > hi else "dip"})
    return out

def detect_anomalies_seasonal(series, lag):
    """Residual from seasonal-naive baseline (value vs same lag ago)."""
    if len(series) <= lag: return []
    residuals = []
    for i in range(lag, len(series)):
        diff = series[i][1] - series[i-lag][1]
        residuals.append((series[i][0], diff))
    if not residuals: return []
    mu = statistics.mean(r[1] for r in residuals)
    sd = statistics.stdev(r[1] for r in residuals) or 1
    out = []
    for ts, r in residuals:
        z = (r - mu) / sd
        if abs(z) > 3:
            out.append({"timestamp": ts.isoformat(),
                        "residual": round(r,2), "z": round(z, 2)})
    return out
```

### Step 4：突变点检测（CUSUM 简化版）

定位“什么时候开始变了”——比单点异常更结构化：

```python
def cusum_change_points(series, drift=0.5):
    """Two-sided CUSUM: cumulative sum of deviations from mean."""
    vals = [v for _, v in series]
    if len(vals) < 10: return []
    mu = statistics.mean(vals)
    sd = statistics.stdev(vals) or 1
    k = drift * sd  # allowance (in std units)

    pos = neg = 0
    pos_max = neg_max = 0
    pos_idx = neg_idx = -1
    change_points = []
    threshold = 4 * sd

    for i, v in enumerate(vals):
        pos = max(0, pos + (v - mu - k))
        neg = min(0, neg + (v - mu + k))
        if pos > pos_max:
            pos_max, pos_idx = pos, i
        if abs(neg) > abs(neg_max):
            neg_max, neg_idx = neg, i
        # Trigger on threshold
        if pos_max > threshold:
            change_points.append({
                "index": pos_idx,
                "timestamp": series[pos_idx][0].isoformat(),
                "direction": "increase",
                "magnitude": round(pos_max/sd, 2),
                "new_mean_after": round(statistics.mean(vals[pos_idx:]), 2),
            })
            pos = pos_max = 0
            pos_idx = -1
        if abs(neg_max) > threshold:
            change_points.append({
                "index": neg_idx,
                "timestamp": series[neg_idx][0].isoformat(),
                "direction": "decrease",
                "magnitude": round(abs(neg_max)/sd, 2),
                "new_mean_after": round(statistics.mean(vals[neg_idx:]), 2),
            })
            neg = neg_max = 0
            neg_idx = -1

    return change_points
```

### Step 5：交叉相关与预测

```python
def cross_correlate(a, b, max_lag=None):
    """Pearson correlation between series a and lagged series b."""
    if len(a) != len(b):
        raise ValueError("series must be aligned")
    n = len(a)
    max_lag = max_lag or n // 2
    results = []
    av = [v for _, v in a]; bv = [v for _, v in b]
    ma = sum(av)/n; mb = sum(bv)/n
    sa = (sum((x-ma)**2 for x in av))**0.5
    sb = (sum((y-mb)**2 for y in bv))**0.5
    if not sa or not sb: return []
    for lag in range(-max_lag, max_lag + 1):
        if lag >= 0:
            x = av[:n-lag]; y = bv[lag:]
        else:
            x = av[-lag:]; y = bv[:n+lag]
        if not x or not y: continue
        mx = sum(x)/len(x); my = sum(y)/len(y)
        num = sum((xi-mx)*(yi-my) for xi, yi in zip(x, y))
        den = (sum((xi-mx)**2 for xi in x) * sum((yi-my)**2 for yi in y))**0.5
        results.append({"lag": lag, "corr": round(num/den, 3)})
    results.sort(key=lambda r: -abs(r["corr"]))
    return results[:5]

def forecast_seasonal_naive(series, horizon, lag):
    """y(t+h) = y(t+h-lag). Robust baseline for any periodic series."""
    vals = [v for _, v in series]
    if len(vals) < lag: return []
    last_ts = series[-1][0]
    bucket = infer_bucket(series)
    out = []
    for h in range(1, horizon + 1):
        ts = last_ts + bucket * h
        out.append({"timestamp": ts.isoformat(),
                    "forecast": vals[-lag + (h-1) % lag]})
    return out

def forecast_holt_linear(series, horizon, alpha=0.3, beta=0.1):
    """Double exponential smoothing with trend. No seasonality."""
    vals = [v for _, v in series]
    if len(vals) < 2: return []
    level = vals[0]
    trend = vals[1] - vals[0]
    for v in vals[1:]:
        prev_level = level
        level = alpha * v + (1 - alpha) * (level + trend)
        trend = beta * (level - prev_level) + (1 - beta) * trend
    bucket = infer_bucket(series)
    last_ts = series[-1][0]
    out = []
    for h in range(1, horizon + 1):
        ts = last_ts + bucket * h
        out.append({"timestamp": ts.isoformat(),
                    "forecast": round(level + h * trend, 2),
                    "lower": round(level + h * trend - 1.96 *
                                   abs(trend) * (h**0.5), 2),
                    "upper": round(level + h * trend + 1.96 *
                                   abs(trend) * (h**0.5), 2)})
    return out
```

### Step 6：组装结构化报告

```markdown
# Time Series Analysis Report / 时间序列分析报告

**Source:** `{filename}` · **Points:** {N} · **Bucket:** {bucket} · **Span:** {first} → {last}

---

## 📈 Trend / 趋势

| Metric | Value |
|---|---|
| Direction | {up/down/flat} |
| Slope per step | {x} |
| Total change | {y}% over {n} steps |
| R² | {r2} (closer to 1 = cleaner trend) |
| 7-step MA (last) | {value} |

**Interpretation:** _Plain-language summary, e.g. "Upward trend, +2.3% per day on average. Last 7-day average is X, vs Y at start."_

## 🔁 Seasonality / 季节性

| Lag (steps) | Autocorrelation |
|---|---|
| 7 (weekly) | {r} |
| 30 (monthly) | {r} |
| 365 (yearly) | {r} |

**Strongest cycle:** lag **{k}** with correlation **{r}** — {strong / weak}.

## ⚠️ Anomalies / 异常点

| Timestamp | Value | Type | Z-score |
|---|---|---|---|
| {ts} | {v} | spike | +{z} |
| {ts} | {v} | dip | -{z} |

**Total anomalies:** {N} (Z-score > 3). **IQR outliers:** {M}.

## 🔀 Change Points / 突变点

| Timestamp | Direction | Magnitude | New mean after |
|---|---|---|---|
| {ts} | decrease | -2.1σ | {v} |
| {ts} | increase | +1.8σ | {v} |

**Interpretation:** _"Series dropped from ~{old} to ~{new} on {date}, likely tied to {hypothesis}."_

## 🔮 Forecast (next {h} steps)

| Method | Used | Reason |
|---|---|---|
| Seasonal-naive | ✓ | Clear {k}-step cycle detected |
| Holt linear | ✓ | R² > 0.5, trend present |

| Timestamp | Forecast | Lower 95% | Upper 95% |
|---|---|---|---|
| {ts} | {v} | {lo} | {hi} |

## 🔗 Cross-Correlation (if 2nd series provided)

| Lag | Correlation |
|---|---|
| {l} | **{r}** ← strongest |
```

---

## Example Invocations / 调用示例

### Example 1：日活异常诊断

```
User: "我的 DAU 从 1/1 到 3/15，附 CSV 是 daily_active_users.csv，
       列是 date 和 dau。找出异常和突变点。"

Hermes 应该：
  1. 用 load_csv 读取，infer_bucket 识别为 1 天
  2. 重采样 sum（每日去重用户已聚合）
  3. linear_trend 输出方向和斜率
  4. detect_anomalies_zscore 找 >3σ 的天数
  5. cusum_change_points 扫描，找到 2/8 的下跌突变
  6. 输出去趋势/季节/异常/突变四点报告
```

### Example 2：广告花费 vs 销售的相关性

```
User: "我有两份 CSV——ad_spend.csv 和 revenue.csv，列名分别是
       date/spend 和 date/revenue。广告投放几天后转化最高？"

Hermes 应该：
  1. 分别 load_csv + resample 到日桶
  2. 对齐到共同时间范围（inner join by date）
  3. cross_correlate 扫描 lag -30..+30
  4. 报告 "lag=3 时相关性最高 +0.72"
  5. 提示用户：广告投放 3 天后转化最强
```

### Example 3：预测下月订阅收入

```
User: "monthly_subs.csv 是过去 18 个月的 MRR，预测下 3 个月。"

Hermes 应该：
  1. load_csv，确认月度桶
  2. detect_seasonality 扫 lag 3..12
  3. 如果季节性弱 + 趋势明显 → Holt linear
  4. 如果强季节性 → seasonal-naive
  5. 输出预测表 + 95% 置信区间
  6. 同时给出"过去 18 个月趋势：+8%/月，R²=0.91"
```

---

## Common Pitfalls / 常见陷阱

| Problem | Solution |
|---|---|
| **时间戳字符串格式多样** | 优先尝试 Unix 整数秒；再按 `COMMON_FORMATS` 顺序试；最后 `fromisoformat` |
| **时区导致 1 天偏移** | 全部 `replace(tzinfo=None)` 转 naive；或归一化到 UTC |
| **数据有缺失日期（gaps）** | resample 时自动补空（mean=NaN 时跳过该桶并报告） |
| **序列太短**（<30 点） | 跳过季节性 / CUSUM，trend 仅报告方向 |
| **重复时间戳** | 同一桶内按 agg 聚合（sum/mean/count），不要直接 append |
| **数值列含货币符号、千分位** | `.replace(",", "").replace("$", "")` 后再 float() |
| **趋势被一个超大异常点主导** | 先 z-score 标记异常 → 用 `series_no_outliers` 跑 trend |
| **预测区间越远越宽** | Holt 区间随 √h 扩张是正常的；>3 步以外置信度低，建议不报 |
| **两个序列长度不一致** | cross_correlate 前按时间戳 outer join + dropna |
| **季节性周期非整数（25h、4.25d）** | 此 skill 只处理整数 lag；告诉用户升级到 `statsmodels` |
| **季节性突变点误报** | CUSUM 阈值 `4*sd` 是经验值；可调 `drift` 提高特异性 |

---

## Verification Checklist / 验证清单

- [ ] 时间戳成功解析为 `datetime`，未识别项列入 `parse_errors`
- [ ] 自动检测到合理桶（分钟/小时/日/周）
- [ ] 数据已按桶重采样，缺失桶在报告中标出
- [ ] 趋势 R² > 0 表示有线性分量；标注方向
- [ ] 季节性扫描覆盖 lag 2 到 N/2，取相关性绝对值 Top 3
- [ ] 异常检测用至少 2 种方法（z-score + IQR），结果交叉验证
- [ ] 突变点报告位置 + 方向 + 前后均值差
- [ ] 预测选择与季节性/趋势检测结论一致
- [ ] 报告包含一段自然语言解读（不要只给数字）
- [ ] 输入样本 <30 点时给出降级说明

---

## Data Sources & Accuracy / 数据来源与精度

**数据来源**：完全基于用户提供的文件。无外部 API 调用。

**精度注意**：
- **OLS 趋势** 只拟合直线；若真实曲线为指数或对数，R² 会偏低，建议对数变换后再拟合
- **自相关** 用 Pearson；只捕捉线性周期；对非正弦型季节性不敏感
- **z-score 异常** 假设分布接近正态；偏态数据会漏报，可先用 `log1p` 变换
- **CUSUM 突变点** 用 4σ 经验阈值；对小样本（<30）极易误报
- **Holt 预测** 不处理季节性；遇强季节性数据改用 seasonal-naive
- **置信区间** 基于线性外推的高斯假设；远离训练范围时不可靠

**依赖**：仅 Python 标准库（`statistics`, `datetime`, `csv`, `json`, `collections`, `re`）。可在任何 Python 3.8+ 环境运行。