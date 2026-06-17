# arXiv 论文摘要: 2401.09670

## 基本信息

| 字段 | 内容 |
|------|------|
| **标题** | DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving |
| **作者** | Yinmin Zhong, Shengyu Liu, Junda Chen, Jianbo Hu, Yibo Zhu, Xuanzhe Liu, Xin Jin, Hao Zhang |
| **发表** | OSDI 2024 |
| **分类** | cs.DC (分布式计算) |
| **链接** | https://arxiv.org/abs/2401.09670 |
| **PDF** | https://arxiv.org/pdf/2401.09670 |

---

## 方法 (Method)

**核心思路：将 LLM 服务的 Prefill（预填充）和 Decoding（解码）阶段进行分离部署。**

- 现有 LLM 服务系统将 Prefill 和 Decoding 两个阶段共置在同一 GPU 上，对所有用户和请求的这两个阶段进行统一批处理。
- DistServe 则将 Prefill 和 Decoding 计算分配到**不同的 GPU**上执行，彻底消除了两者之间的互相干扰。

**关键技术点：**

1. **解耦资源分配** — 针对 Prefill 阶段（影响 TTFT，首 Token 延迟）和 Decoding 阶段（影响 TPOT，每个输出 Token 的时间）分别独立优化资源分配和并行策略。
2. **带宽感知部署** — 根据服务集群的带宽情况，合理放置 Prefill 和 Decoding 两个阶段的位置，以最小化解耦带来的通信开销。
3. **联合优化** — 在应用的 TTFT 和 TPOT 延迟要求下，协同优化两阶段的资源配置和并行方案。

---

## 结果 (Results)

在多种主流 LLM、应用场景和延迟约束下：

| 指标 | 提升幅度 |
|------|---------|
| **请求吞吐量** | 比现有最先进系统提升 **7.4 倍** |
| **SLO 收紧能力** | 可支持 **12.6 倍**更严格的延迟约束 |
| **延迟满足率** | 在 > 90% 的请求中保持在延迟约束范围内 |

评估覆盖了各类流行的 LLM 模型、应用场景（如对话、代码生成等）和不同的延迟要求（TTFT + TPOT）。

---

## 优势 (Strengths)

1. **根本性解决了阶段干扰问题** — 通过物理分离 Prefill 和 Decoding，避免了两者在同一 GPU 上竞争计算资源导致的性能抖动。
2. **延迟感知的优化** — 不像传统方法需要牺牲一种延迟来满足另一种，DistServe 能为 TTFT 和 TPOT 分别设定独立的目标并同时满足。
3. **避免过度配置** — 现有系统为达到双重要求往往需要过度配置 GPU 资源，DistServe 通过解耦显著提高了资源利用率。
4. **实用性强** — 已被 OSDI 2024 接收，经过严格的学术评审，实验结果来自真实部署场景。

---

## 局限性 (Limitations)

1. **引入了通信开销** — Prefill 和 Decoding 分离后，两阶段之间需要网络通信来传递中间状态（KV Cache 等），对集群带宽有较高要求。
2. **系统复杂度增加** — 从共置架构变为分离架构，需要额外的调度、负载均衡和故障处理机制。
3. **对小型模型/低负载场景可能不够友好** — 分离部署带来的额外通信和调度开销在小规模部署中可能抵消收益。
4. **未讨论训练场景** — 本文聚焦 LLM 推理服务，不涉及训练阶段的 Prefill-Decoding 优化。

---

*生成日期: 2026-06-17*
*数据来源: arXiv API (export.arxiv.org)*
