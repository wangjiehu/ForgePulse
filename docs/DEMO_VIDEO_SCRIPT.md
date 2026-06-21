# Demo Video Script

目标时长：90 秒。

## 0-10s: Opening

画面：ForgePulse 工作台首页。

旁白：

> 这是 ForgePulse，一个面向新能源电池产线的设备异常诊断 Agent。它不是聊天机器人，而是工程师工作台。

## 10-25s: Problem Setup

画面：左侧五个案例列表。

旁白：

> 电池涂布产线异常通常不是单一报警。温度、张力、风机、驱动电流和膜厚可能同时变化，工程师需要从多个系统拼接证据。

## 25-45s: Case 1 Diagnosis

画面：选择 `coating_line_dryer_tension_001`。

展示：

- Data quality；
- Diagnostic process；
- Timeline。

旁白：

> ForgePulse 首先校验数据，然后检测传感器异常、关联报警、检索 SOP 和维修记录，最后生成根因排序。

## 45-60s: Evidence-grounded Root Cause

画面：Root Cause Ranking + Evidence Chain。

旁白：

> 每个根因都有证据链。比如干燥 2 区温控回路异常，关联 DRY-122 报警、温度传感器峰值和历史维修记录 M-2026-041。

## 60-75s: Actions and Report

画面：Recommended Actions、Work Order Draft、Export Report。

旁白：

> 系统按角色生成处置动作，输出维修工单草案，并可导出复盘报告。所有动作都保留安全边界，需要现场工程师确认。

## 75-85s: Multi-case Proof

画面：快速切换 airflow、证据不足和证据冲突案例。

旁白：

> 项目内置五个工业案例，不只覆盖温控、风机和驱动阻力，也验证了证据不足时主动停止、证据冲突时请求核验。71 项自动检查全部通过。

## 85-90s: Closing

画面：Business value 或报告页面。

旁白：

> ForgePulse 的目标是成为厂内只读试点的工业诊断 Agent，帮助工程师更快定位故障、沉淀经验、降低复盘成本。

## Recording Checklist

- 后端先启动在 `localhost:8000`。
- 前端启动在 `localhost:5173`。
- 浏览器缩放保持 100%。
- 先清空无关标签页。
- 每个页面停留足够让评委看清文字。
- 不展示任何真实 Token 或私人信息。
