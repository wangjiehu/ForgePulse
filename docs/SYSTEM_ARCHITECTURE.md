# System Architecture

## Layers

```text
Input Assets
  |-- sensor csv
  |-- alarm log
  |-- SOP/manual
  |-- maintenance records
  |-- operator note
       |
       v
Data Layer
  |-- case loader
  |-- schema validator
  |-- document chunker
       |
       v
Analysis Layer
  |-- time-series anomaly detector
  |-- alarm correlation
  |-- event timeline builder
       |
       v
Knowledge Layer
  |-- SOP retriever
  |-- maintenance history retriever
  |-- fault-mode matcher
       |
       v
Agent Layer
  |-- diagnosis planner
  |-- root-cause ranker
  |-- action planner
  |-- report composer
       |
       v
Experience Layer
  |-- engineer dashboard
  |-- evidence view
  |-- work order
  |-- postmortem report
```

## Runtime Modes

### Offline Demo Mode

- 使用仓库内合成样例数据。
- 使用确定性规则和模板输出。
- 不需要外部模型 Token。

### LLM Assisted Mode

- 在 deterministic 结果上调用模型生成更自然的解释和报告。
- LLM 不直接决定事实，只组织和补充推理。
- 输出必须通过 schema 校验。

### Industrial Deployment Mode

- 接入工厂 MES/SCADA/日志系统。
- 使用本地模型或私有化服务。
- 可部署到边缘节点或厂内服务器。

## Backend Modules

- `case_loader`: 读取 case manifest 和关联文件。
- `sensor_analyzer`: 检测阈值越界、漂移、突变和关联波动。
- `alarm_parser`: 解析报警码和时间窗口。
- `retriever`: 检索 SOP 与维修记录。
- `diagnosis_engine`: 组合事实、证据、假设和建议。
- `report_writer`: 生成工单和复盘报告。

## Frontend Panels

- Case Selector
- Signal Overview
- Event Timeline
- Root Cause Ranking
- Evidence Drawer
- Work Order Draft
- Postmortem Report
