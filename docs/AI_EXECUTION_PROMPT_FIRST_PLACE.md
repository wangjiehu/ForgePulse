# AI Execution Prompt: First-place / Market-ready ForgePulse

把下面提示词交给另一个 AI 使用。

```text
你现在接手项目：
C:\Users\24377\Desktop\新建文件夹\ForgePulse

目标：
把 ForgePulse 从可运行 MVP 升级到“比赛第一梯队 + 可市场化试点”的工业 Agent 产品原型。不要只做一个漂亮 demo，要做能被评委和企业相信的 Evidence-grounded Maintenance Agent。

必须先完整阅读这些文件：
- README.md
- DELIVERY_CHECKLIST.md
- docs/FIRST_PLACE_MARKET_READY_PLAN.md
- docs/MARKET_READY_ROADMAP.md
- docs/AI_BUILD_PROTOCOL.md
- docs/SYSTEM_ARCHITECTURE.md
- docs/AGENT_WORKFLOW.md
- docs/DATA_CONTRACTS.md
- docs/EVALUATION_PLAN.md
- docs/IMPLEMENTATION_GUIDE.md
- data/samples/coating_line_case/*

核心定位：
ForgePulse 是面向新能源电池涂布产线的设备异常诊断与维护决策 Agent。它读取传感器时序、报警日志、SOP、维修记录和现场描述，输出异常时间线、证据链、根因排序、角色化处置动作、维修工单、复盘报告和价值估算。

不可改变的方向：
1. 不要改成金融、医疗、SRE 或泛办公助手。
2. 不要做成普通聊天机器人。
3. 第一屏必须是工程师工作台。
4. 第一版必须完全 offline 可运行，不依赖任何模型 Token。
5. 不要写入真实 API Key、Token、账号、密码或敏感数据。
6. 诊断结论必须引用真实输入证据，禁止编造证据。
7. 不要声称能替代现场安全责任人或自动控制设备。

Python 规则：
如果需要运行 Python，先动态发现 Conda：
- Get-Command conda
- conda env list
然后询问用户使用哪个 Conda 环境，除非用户已经明确指定。

第一阶段：验证现有系统
1. 在用户指定 Conda 环境里安装后端依赖：pip install -e ".[dev]"
2. 跑 pytest -v，修复失败。
3. 启动 FastAPI，验证：
   - GET /health
   - GET /cases
   - GET /cases/coating_line_dryer_tension_001/diagnosis
4. 前端执行 npm install、npm run build、npm audit。
5. 启动前后端，做端到端浏览器检查。

第二阶段：补强为第一名级别
请按顺序实现：

1. 多案例
   - 新增 data/samples/coating_line_airflow_case
   - 新增 data/samples/coating_line_drive_resistance_case
   - 每个案例必须有：
     - case_manifest.json
     - sensor_readings.csv
     - alarms.csv
     - sop markdown
     - maintenance_records markdown
     - golden_expectations.json
   - 后端 list_cases 自动发现所有案例。
   - 前端可切换案例并展示不同诊断。

2. 数据校验
   - 增加 schema/data validator。
   - 缺列、空文件、未知 case_id 时返回明确错误。
   - 增加测试覆盖。

3. 诊断核心升级
   - 增加 fault_modes.json，定义常见故障模式、相关指标、报警码、建议动作。
   - 增加 root cause score breakdown：
     - alarm_match
     - sensor_correlation
     - sop_match
     - maintenance_similarity
     - quality_risk
   - 每个根因显示评分组成，而不是只显示 confidence。
   - 增加 diagnostic_process trace：
     - data_validation
     - anomaly_detection
     - alarm_correlation
     - sop_retrieval
     - maintenance_similarity
     - root_cause_ranking
     - action_planning

4. Evidence Graph
   - 后端输出 Root Cause -> Evidence -> Source -> Action 的结构。
   - 前端展示 evidence graph/table。
   - 所有 evidence_ids 必须真实存在。

5. Report Export
   - 后端增加 Markdown 报告导出接口。
   - 前端增加“Export Report”按钮。
   - 报告包含：事件摘要、时间线、根因、证据、处置动作、工单、复盘、限制说明。

6. 角色化动作
   - actions 按角色分组：
     - equipment engineer
     - quality engineer
     - production supervisor
     - safety reviewer
   - 前端显示 role-based action board。

7. 价值估算
   - 增加 business value estimate：
     - estimated_triage_time_saved
     - avoided_downtime_risk
     - affected_material_window
     - knowledge_reuse_value
   - 表述必须保守，写成试点目标或估算，不写成已验证承诺。

8. 自动评测
   - 新增 evaluation/golden_cases.json
   - 新增 evaluation/evaluate_cases.py
   - 检查：
     - root cause 是否命中 expected
     - required evidence 是否存在
     - required actions 是否存在
     - forbidden claims 是否没有出现
     - all evidence ids valid
   - README 写入评测命令和示例结果。

9. 市场化文档
   - 新增 docs/BUSINESS_VALUE.md
   - 新增 docs/PILOT_DEPLOYMENT_PLAN.md
   - 新增 docs/SECURITY_AND_SAFETY_BOUNDARIES.md
   - 新增 docs/PITCH_SCRIPT.md
   - 新增 docs/DEMO_VIDEO_SCRIPT.md
   - 明确厂内只读接入 MES/SCADA/质量系统路线、数据不出厂、Ascend/NPU 本地推理价值。

10. UI 打磨
   - 保持工程师工作台风格，不要营销页。
   - 增加 data quality panel、diagnostic process panel、evidence graph、role action board、value estimate card。
   - 保证桌面和移动视口不重叠、不溢出。
   - 使用 lucide-react 图标。

质量门槛：
- npm run build 通过。
- npm audit 0 vulnerabilities。
- pytest -v 通过。
- 自动评测通过。
- 前后端端到端可演示。
- README 能让非技术评委 1 分钟内理解价值。
- 不提交 node_modules、dist、__pycache__、.atomcode、.claude。

最终汇报：
请按以下格式汇报：
1. 已完成内容
2. 修改文件
3. 验证结果
4. 剩余风险
5. 下一步建议
```
