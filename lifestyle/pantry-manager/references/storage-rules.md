# 存储与计算规则

## 批次而不是商品总量

同一标准化名称的每次购买都创建独立批次。展示可以汇总，日期判断和扣减必须保留批次粒度。

## 最小字段

- `id`: 稳定且唯一，例如 `milk-20260729-a`
- `name`: 标准化名称
- `display_name`: 用户习惯的展示名
- `quantity`: 非负数字
- `unit`: `g|kg|ml|l|count|pack`
- `location`: `pantry|fridge|freezer|custom`
- `status`: `active|consumed|spoiled|discarded|reserved`
- `date_type`: `use_by|best_before|sell_by|unknown`
- `expires_at`: ISO 日期或 `null`
- `estimated_expiry`: 布尔值
- `created_at`, `updated_at`: ISO 时间

## 日期优先级

1. 用户确认的包装 `use by`
2. 用户确认的 `best before`
3. 用户确认的购买/开封日期加明确规则
4. 保守估算，并标记 `estimated_expiry: true`
5. 无可靠依据时保持 `null`

## 扣减规则

- 只扣 `status=active`。
- 默认按有效到期日升序；无日期排最后。
- 相同日期按 `opened_at`、`created_at` 升序。
- 数量不得小于 0。
- 跨批次扣减要在历史中逐项记录。
- 单位仅在有明确换算时转换：`1kg=1000g`、`1l=1000ml`。`pack` 与重量不能默认互换。

## 同义词

可以将 `green onion`、`scallion` 映射到同一规范名，但原始展示名和用户语言应保留。品牌、脂肪比例、过敏原或用途不同的商品不要仅凭名称合并。

## 安全边界

日期不是传感器。停电、冷链中断、包装破损、霉菌和交叉污染必须单独记录。Agent 只能给风险提示，不能证明食物安全。
