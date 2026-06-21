# ForgePulse Project Planning

当前日期：2026-06-16

规划基准：不按赶时间的临时 demo 设计，而按“AI 可以持续完成、项目真实可行、有行业价值、可被评审理解”的标准设计。

## 1. Core Thesis

ForgePulse 的核心判断是：

> 在行业 Agent 比赛中，最有竞争力的项目不是功能最多的通用助手，而是能把一个具体行业工作流闭环跑通的垂直 Agent。

所以本项目只聚焦一个明确场景：

> 新能源电池涂布产线设备异常诊断和维护决策。

它可以向辊压、分切、化成、PACK 等环节扩展，但第一版不泛化。

## 2. Why This Direction Still Holds

用户补充了两个重要约束：

- 项目尽量由 AI 完成。
- 没有紧迫时间要求，重点是框架可行、合适、有价值。

在这个约束下，ForgePulse 方向比金融、医疗、泛 SRE 更稳：

- 金融和医疗价值高，但真实规则、合规、数据隐私和专业责任边界更难由 AI 安全补齐。
- 泛 SRE 更容易做，但行业属性弱，和赛题“行业业务强相关”不够贴。
- 新能源制造可以用合成数据复现真实逻辑，能展示行业痛点，也能控制安全和合规风险。

## 3. Product Boundaries

### Must Have

- 行业场景必须明确到产线工段。
- 输入必须包含至少两类结构化数据和一类非结构化文档。
- 输出必须包含证据链，不能只给自然语言建议。
- 诊断必须区分“数据事实”“检索依据”“推理判断”“行动建议”。
- 演示必须稳定可复现。

### Should Have

- 工单草案生成。
- 复盘报告生成。
- 量化收益估算。
- 多轮追问解释。
- 昇腾/NPU 落地路线说明。

### Must Not Have

- 不给无证据根因结论。
- 不伪装成真实专家系统。
- 不使用真实敏感数据。
- 不把聊天框当作主要产品形态。

## 4. Architecture Strategy

ForgePulse 分成五层：

1. Data Layer: 样例数据、SOP、维修记录、案例 manifest。
2. Analysis Layer: 时序异常检测、日志解析、时间线重建。
3. Knowledge Layer: SOP 和维修记录检索。
4. Agent Layer: 根因推理、处置规划、报告生成。
5. Experience Layer: 工程师工作台 UI。

第一阶段可以用确定性规则和模板稳定输出，第二阶段再接入 LLM provider。这样即使模型不可用，演示也不会完全失败。

## 5. AI Completion Strategy

因为项目目标是尽量由 AI 完成，框架要降低 AI 犯错概率：

- 用清晰的数据契约约束输入输出。
- 用样例数据固定演示路径。
- 用评测用例约束诊断质量。
- 用 Agent 提示词明确禁止编造证据。
- 用结构化 JSON 作为后端和前端之间的接口。
- 用文档把业务假设和合成数据边界写清楚。

## 6. First Build Milestone

最小可运行闭环：

1. 后端读取 `data/samples/coating_line_case/case_manifest.json`。
2. 后端解析传感器、报警、SOP、维修记录。
3. 后端输出结构化诊断 JSON。
4. 前端展示四个区块：
   - 异常时间线
   - 根因候选
   - 证据链
   - 工单和报告
5. README 说明如何运行和如何替换数据。

## 7. Long-term Roadmap

### Phase 1: Deterministic Demo

- 静态样例数据。
- 规则检测异常。
- 关键词检索 SOP。
- 模板生成诊断报告。
- 前端工作台展示。

### Phase 2: LLM-assisted Diagnosis

- 接入 OpenAI-compatible provider。
- 将规则结果作为上下文交给 LLM。
- 强制结构化输出。
- 加入证据引用校验。

### Phase 3: Industrial Knowledge Base

- 支持多案例。
- 支持知识文档增量导入。
- 支持历史维修记录归因。
- 支持故障模式库。

### Phase 4: Ascend/NPU Route

- 本地模型推理。
- 边缘节点部署。
- 批量日志离线分析。
- 低延迟报警摘要。

## 8. Definition of Done

项目框架完成的标准：

- 新开发者或 AI Agent 能根据文档继续实现。
- 数据格式、接口格式、报告格式都有契约。
- 样例案例能支撑完整 demo。
- 评测标准能判断输出好坏。
- 架构能解释为什么这不是普通聊天机器人。
