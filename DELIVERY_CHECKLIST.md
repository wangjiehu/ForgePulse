# ForgePulse Delivery Checklist

## 1. Framework Checklist

- [x] Agent 名称和定位
- [x] 方向复核与选择理由
- [x] 项目目录结构
- [x] 全 AI 构建协议
- [x] 系统架构文档
- [x] Agent 工作流文档
- [x] 数据契约文档
- [x] 评测方案
- [x] 演示故事板
- [x] 昇腾/NPU 集成路线
- [x] 样例案例 manifest
- [x] 样例传感器 CSV
- [x] 样例报警日志
- [x] 样例 SOP
- [x] 样例维修记录
- [x] 后端代码骨架
- [x] 前端代码骨架
- [x] 示例报告

## 2. Implementation Checklist

- [x] 后端实现 case loader
- [x] 后端实现 sensor analyzer（阈值检测 + 持续漂移检测）
- [x] 后端实现 alarm parser
- [x] 后端实现 document retriever（SOP + 维修记录关键词匹配）
- [x] 后端实现 deterministic diagnosis engine（故障模式库匹配 + 加权评分）
- [x] 后端实现 report generator（Markdown 导出）
- [x] 前端实现工程师工作台布局
- [x] 前端实现案例选择面板
- [x] 前端实现异常时间线面板
- [x] 前端实现根因排序面板（含 score breakdown）
- [x] 前端实现证据链面板
- [x] 前端实现推荐动作面板（含 role-based）
- [x] 前端实现工单草案面板
- [x] 前端实现复盘摘要面板
- [x] 前端实现数据质量面板
- [x] 前端实现诊断过程追踪面板
- [x] 前端实现价值估算卡片
- [x] 前端实现报告导出按钮
- [x] 前端从后端 API 获取数据（非硬编码）
- [x] README 包含运行命令
- [x] 增加测试集（83 tests passing）
- [x] 增加评测脚本和黄金案例
- [x] 前端增加构建产物 smoke 验收脚本
- [x] 生成 5 份可直接审阅的 Markdown 样例报告
- [x] 生成 9 页可编辑路演 PPT，并完成逐页渲染 QA

## 3. Quality Gates

- [x] 输出是否引用了真实输入证据 — evidence_ids 均指向真实数据和文档
- [x] 是否区分事实、推理和建议 — timeline/evidence 为事实，root_cause 为推理，actions 为建议
- [x] 是否能在无模型 Token 的情况下运行基础 demo — 纯确定性规则引擎
- [x] 是否没有把敏感信息写入仓库 — 无 API Key / Token / 密码
- [x] UI 是否像工程师工作台 — 工程师工作台布局，非聊天框或营销页
- [x] README 是否能让评委快速理解行业价值 — 包含运行说明和 API 文档
- [x] 桌面和移动宽度下布局不重叠、不溢出 — 响应式网格布局
- [x] 前端构建产物是否包含关键工作台模块 — smoke 验证通过
- [x] 公开目录是否排除本地状态和依赖产物 — 已清理 node_modules/dist/cache/tool-state

## 4. Cases & Evaluation

- [x] Case 1: coating_line_dryer_tension_001 — 干燥2区温控回路不稳定
- [x] Case 2: coating_line_airflow_002 — 风机变频频率异常
- [x] Case 3: coating_line_drive_resistance_003 — 驱动辊污染阻力
- [x] golden_cases.json 评测期望
- [x] evaluate_cases.py 评测脚本
- [x] 5 个案例评测全部通过（71/71）
- [x] 增加证据不足和证据冲突负向案例
- [x] 增加反事实、确定性、引用完整性和 golden 隔离评测
- [x] 评测检查每个案例的 RC-001 是否命中预期主根因

## 5. Key Evidence Verified

- [x] DRY-122 报警证据（干燥2区温度异常）
- [x] TEN-204 报警证据（张力闭环响应滞后）
- [x] QCS-318 报警证据（膜厚漂移/良率风险）
- [x] M-2026-041 维修记录证据
- [x] 传感器温度、张力、膜厚异常数据

## 6. Submission Artifacts

最终提交建议包括：

- 代码仓库
- README（含运行说明和 API 文档）
- 部署说明
- 演示脚本（backend + frontend quick start）
- 样例数据说明（5 个工业案例）
- 结构化诊断报告（API 可导出 Markdown）
- 架构图（docs/SYSTEM_ARCHITECTURE.md）
- 评测结果（evaluation/evaluation_results.json）

## 7. First-place / Market-ready Upgrade

- [x] 后端 pytest 通过（83 tests）
- [x] 前端 Vite 构建通过
- [x] npm audit 通过（0 vulnerabilities）
- [x] API 验证通过（health/cases/diagnosis/report/fault-modes/404）
- [x] 新增 2 个高质量工业案例（airflow + drive）
- [x] 每个案例新增 golden_expectations.json
- [x] 增加 fault_modes.json（故障模式库）
- [x] 增加 root cause score breakdown
- [x] 增加 diagnostic process trace
- [x] 增加 evidence links graph
- [x] 增加 Markdown 报告导出 API
- [x] 前端增加 Export Report 按钮
- [x] 前端增加 data quality panel
- [x] 前端增加 role-based action board
- [x] 前端增加 value estimate card
- [x] 增加 evaluation/golden_cases.json
- [x] 增加 evaluation/evaluate_cases.py
- [x] README 展示评测命令和结果
- [x] README 增加 3 分钟 demo 路径、验证快照和样例报告链接
- [x] 生成 reports/generated_samples/ 五份最终报告
- [x] 公开发布前清理本地工具状态、缓存、构建产物和依赖目录
- [x] 新增 BUSINESS_VALUE.md
- [x] 新增 PILOT_DEPLOYMENT_PLAN.md
- [x] 新增 SECURITY_AND_SAFETY_BOUNDARIES.md
- [x] 新增 PITCH_SCRIPT.md
- [x] 新增 DEMO_VIDEO_SCRIPT.md
- [x] 新增 PUBLIC_RELEASE_CHECKLIST.md
- [x] 新增 NEXT_STRATEGIC_WORK_PLAN.md
- [x] 新增 AI_BUILD_LOG.md
- [x] 新增一键 verify/run/stop PowerShell 脚本
- [x] 新增严格案例 validate/import/diagnose CLI
- [x] 新增可选 narrative-only model provider 及 Evidence ID 防护
- [x] 新增 deliverables/ForgePulse-Agent-Hackathon.pptx
