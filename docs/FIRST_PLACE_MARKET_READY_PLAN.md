# First-place and Market-ready Plan

ForgePulse 当前是一个可运行 MVP 雏形，不是第一名级别作品。要达到“比赛第一梯队，并具备市场化试点价值”，必须把它从单案例 demo 提升为 **工业诊断 Agent 产品原型**。

> **Implementation status (updated 2026-06).** 以下能力已落地，不再是规划：
> - **真 Agent 推理层**：诊断循环现接入 OpenAI 兼容 LLM 作为咨询性复核层
>   （`model_provider.reason` → `AgentReasoning`），双层架构保证确定性结论不被覆盖，
>   证据/候选 ID 经白名单 + `_sanitize_reasoning` 双重校验，失败回退确定性原文。
>   见 `docs/AGENT_WORKFLOW.md`。`scripts/verify_agent.py` 可端到端验证真 LLM 通路。
> - **运行时安全**：API key 鉴权 + RBAC + 滑动窗口限流 + 结构化审计日志
>   （`security.py`）。见 `docs/SECURITY_AND_SAFETY_BOUNDARIES.md`。
> - **前端健壮性**：组件拆分、空状态、错误重试、错误边界、骨架屏、规则表驱动的产线
>   状态、AI 复核 UI，并补齐 vitest 前端测试。
> - **测试与评估**：后端 92 测试 + 评估 76/76（含 offline 不附加 LLM 的新检查）。
>
> 仍未做（按用户决策暂缓）：Docker/云部署化、工厂 SCADA/OPC-UA 真实连接器、
> Ascend NPU 本地推理、性能压测。

## 1. Winning Thesis

比赛里普通项目会做：

- 一个聊天框。
- 一个单场景 demo。
- 几条漂亮但不可验证的 LLM 建议。

ForgePulse 要做成：

> 一个面向新能源电池产线的 Evidence-grounded Maintenance Agent，可以把时序数据、报警、SOP、维修记录和现场描述转成可追溯诊断、工单、复盘和价值评估。

核心差异不是“用了大模型”，而是：

- 诊断有证据。
- 推理有过程。
- 建议能落到工单。
- 输出能被评测。
- 架构能落到厂内边缘部署。

## 2. First-place Bar

### Must reach

- 至少 3 个高质量案例，而不是 1 个固定样例。
- 每个案例都有传感器、报警、SOP、维修记录、预期诊断。
- 前端工作台能切换案例并展示差异化诊断。
- 后端有数据契约校验和错误处理。
- 诊断输出包含事实、证据、假设、行动、限制。
- 有可导出的 Markdown/PDF 风格报告。
- 有评测脚本，能自动验证 evidence id、根因命中、行动完整性。
- README 包含行业痛点、产品能力、运行方式、演示路径、市场价值。
- 有 90 秒 demo 脚本和路演讲稿。

### Should reach

- 支持 LLM provider，但不依赖 LLM 才能运行。
- 支持多种故障类型：温控、张力、风机、质量漂移、设备电流异常。
- 有故障模式库 `fault_modes.json`。
- 有收益估算模块：MTTR 降低、停机损失避免、质量风险隔离。
- 有 Ascend/NPU 本地化部署页面或说明。
- UI 有“诊断过程视图”，不只是结果面板。

### Must not claim

- 不声称已经真实工厂投产。
- 不声称可以自动控制设备。
- 不声称替代设备工程师或安全流程。
- 不使用真实客户数据。

## 3. Product Differentiators

### Evidence Graph

将每个结论关联到数据证据：

```text
Root Cause -> Evidence -> Source -> Timestamp/Section -> Action
```

评委应能看到：为什么这个 Agent 可信。

### Diagnostic Process View

展示 Agent 的推理链，但不是暴露随意的 LLM chain-of-thought。应展示工程化步骤：

1. Data validation
2. Signal anomaly detection
3. Alarm correlation
4. SOP retrieval
5. Maintenance similarity
6. Root-cause ranking
7. Action planning
8. Report generation

### Multi-case Benchmark

用多个案例证明不是硬编码：

- Case A: 涂布干燥段温控 + 张力耦合异常。
- Case B: 风机频率波动导致干燥温度漂移。
- Case C: 驱动电流升高 + 张力异常，疑似辊系污染或机械阻力增加。

### Pilot-ready Packaging

让项目看起来能进入企业试点：

- API 清晰。
- 数据契约清晰。
- 部署说明清晰。
- 隐私和安全边界清晰。
- 试点接入路线清晰。

## 4. Market-ready Product Scope

第一版不能做成真正商业系统，但要达到 **pilot-ready**：

| Area | MVP | First-place / Pilot-ready |
|---|---|---|
| Data | 1 个样例 | 3-5 个案例 + schema 校验 |
| Diagnosis | 规则模板 | 规则 + 检索 + 可选 LLM + 评分解释 |
| UI | 工作台展示 | 工程师可用的完整闭环 |
| Report | 示例报告 | 一键导出诊断报告和工单 |
| Eval | 单元测试 | 自动评测基准 + golden expectations |
| Business | 简短价值 | MTTR/停机/良率收益估算 |
| Deployment | 本地运行 | 厂内边缘部署和 Ascend 路线 |

## 5. Architecture Upgrade

### Data Layer

- `case_manifest.json`
- `sensor_readings.csv`
- `alarms.csv`
- `sop.md`
- `maintenance_records.md`
- `golden_expectations.json`

### Intelligence Layer

- `validator`: 检查数据完整性。
- `analyzer`: 检测异常。
- `correlator`: 将报警、时序和质量事件关联。
- `retriever`: 检索 SOP 和历史记录。
- `fault_ranker`: 计算根因候选分数。
- `action_planner`: 生成排查、维修、质量、安全动作。
- `report_generator`: 导出报告。

### Agent Layer

LLM 只做增强，不做唯一判断：

- 生成自然语言解释。
- 归纳复盘报告。
- 支持工程师追问。
- 将结构化事实转成答辩材料。

### Experience Layer

必须像工程师系统：

- Case switcher
- Data quality panel
- Diagnostic process panel
- Evidence graph/table
- Root-cause ranking
- Actions split by role
- Work order draft
- Report export
- Value estimate

## 6. Evaluation Upgrade

必须建立 `evaluation/golden_cases.json`，每个案例定义：

- expected root cause
- acceptable secondary causes
- required evidence
- required actions
- forbidden claims

评测脚本至少检查：

- 所有 evidence id 存在。
- 根因命中 golden expectation。
- 报警码证据齐全。
- 工单任务非空。
- limitation 包含人工确认和安全边界。

## 7. Business Story

目标行业价值表述：

> 对电池制造企业，ForgePulse 不是替代设备工程师，而是把分散在报警系统、质量系统、SOP 和维修经验里的线索整合成可执行诊断，帮助新工程师更快定位故障，帮助老工程师沉淀经验，帮助主管复盘停机和质量风险。

可量化但保守的价值口径：

- 缩短初步排障时间 30%-50%。
- 降低重复故障沟通成本。
- 缩短新工程师上手周期。
- 提升复盘报告一致性。
- 降低异常物料漏检风险。

注意：这些是试点目标，不是已验证承诺。

## 8. Submission Package

最终提交应包含：

- 可运行代码。
- 5 个案例，其中包含证据不足和证据冲突负向案例。
- 自动评测输出。
- README。
- 产业价值说明。
- 架构图。
- 90 秒 demo 脚本。
- 5 分钟路演讲稿。
- 1 份导出的诊断报告。
- 1 份试点落地路线。

## 9. Order of Work

按影响力排序：

1. 跑通后端测试和 API。
2. 补 2 个新案例。
3. 加 golden expectations 和评测脚本。
4. 加 report export API 和前端按钮。
5. 前端加诊断过程视图和价值估算。
6. 加数据校验和错误态。
7. 打磨 README、演示脚本、路演稿。
8. 可选接入 LLM provider。
9. 可选加 Ascend/NPU 演示说明页。
