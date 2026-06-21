# Market-ready Roadmap

ForgePulse 的市场化目标不是立刻成为生产级控制系统，而是达到 **pilot-ready industrial Agent**：可以给制造企业、评委或合作方演示清楚，并能说明如何接入真实工厂数据做试点。

## Phase 0: Validation Baseline

目标：确认现有最小闭环可靠。

交付：

- 后端 pytest 全通过。
- 前端 production build 通过。
- 本地端到端联调通过。
- API 返回数据与前端展示一致。
- npm audit 为 0。

退出标准：

- 演示时不会出现空白页、API 错误、证据缺失或构建失败。

## Phase 1: Multi-case Industrial Benchmark

目标：摆脱单案例 demo 感。

新增案例：

1. `coating_line_dryer_tension_001`
   - 已有：温控和张力耦合异常。

2. `coating_line_airflow_002`
   - 风机频率下降、局部温度漂移、干燥不均风险。

3. `coating_line_drive_resistance_003`
   - 驱动电流升高、张力波动、疑似辊系污染或机械阻力增加。

4. `coating_line_incomplete_evidence_004`
   - 缺少关键温度字段，要求 Agent 主动停止确认并请求补数。

5. `coating_line_conflicting_evidence_005`
   - 报警与传感器证据冲突，要求 Agent 请求现场核验。

交付：

- 每个案例都有 manifest、sensor csv、alarms csv、SOP、maintenance records、golden expectations。
- 前端可以切换案例。
- 后端按案例生成不同诊断。
- 负向案例能稳定输出保守状态和置信度上限。

## Phase 2: Evidence-grounded Agent Core

目标：让 Agent 可信，而不是像模板。

交付：

- evidence graph 数据结构。
- root cause score breakdown。
- diagnostic process trace。
- action planner 分角色输出：
  - equipment engineer
  - quality engineer
  - production supervisor
  - safety reviewer
- report export endpoint。

退出标准：

- 每个根因都能解释“为什么排这个优先级”。
- 每个行动都能连接到根因或安全要求。

## Phase 3: Product-grade Workbench

目标：让 UI 像真实工业工具。

交付：

- Data quality panel。
- Diagnostic process panel。
- Evidence graph/table。
- Root-cause score explanation。
- Role-based action board。
- Work order export。
- Postmortem report export。
- Value estimate card。
- Empty/error/loading states。
- Mobile and desktop viewport QA。

退出标准：

- 评委一眼看到这是行业工作台，不是网页模板。
- 现场演示 3-5 分钟能完整闭环。

## Phase 4: Evaluation and Trust

目标：证明不是靠写死。

交付：

- `evaluation/golden_cases.json`
- `evaluation/evaluate_cases.py`
- 测试覆盖：
  - schema validation
  - evidence integrity
  - root cause hit rate
  - required actions
  - forbidden claims
- README 展示评测结果。

退出标准：

- 自动评测给出清晰 pass/fail。
- 新增案例后能快速发现诊断退化。

## Phase 5: Market Narrative and Pilot Plan

目标：达到“可投入市场试点”的表达强度。

交付：

- `docs/BUSINESS_VALUE.md`
- `docs/PILOT_DEPLOYMENT_PLAN.md`
- `docs/SECURITY_AND_SAFETY_BOUNDARIES.md`
- `docs/PITCH_SCRIPT.md`
- 架构图。
- 90 秒 demo 脚本。

试点落地说明应覆盖：

- 接入 MES/SCADA/质量系统的只读路线。
- 数据脱敏和厂内部署。
- 角色权限。
- 安全边界。
- Ascend/NPU 本地推理路线。
- 试点指标：MTTR、重复故障率、报告生成时间、异常物料隔离及时性。

## Phase 6: Optional LLM and Ascend Enhancement

目标：让 Agent 更智能，但不破坏可控性。

交付：

- `ModelProvider` 接口实现。
- OpenAI-compatible provider adapter。
- LLM 输出 schema validation。
- Evidence guardrail。
- Ascend/NPU integration notes or demo stub。

原则：

- deterministic engine 是可信基础。
- LLM 是解释和交互增强。
- 任何 LLM 输出必须可追溯到 evidence。
