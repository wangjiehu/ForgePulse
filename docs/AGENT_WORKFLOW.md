# Agent Workflow

## Goal

ForgePulse 的 Agent 目标不是聊天，而是完成设备异常诊断工作流。

## Workflow

1. Intake
   - 读取案例 manifest。
   - 确认可用输入。
   - 标记缺失数据。

2. Normalize
   - 统一时间格式。
   - 对齐传感器和报警时间窗口。
   - 将 SOP 和维修记录切片。

3. Detect
   - 检查阈值越界。
   - 检查短时间突变。
   - 检查多变量同步波动。

4. Correlate
   - 将异常点与报警码关联。
   - 查找异常前后的人工记录。
   - 检索相似维修记录。

5. Diagnose
   - 生成根因候选。
   - 关联每个候选的证据。
   - 给出置信度和优先级。

6. Plan
   - 给出不停机检查项。
   - 给出需要停机确认的检查项。
   - 给出备件、安全和升级建议。

7. Deliver
   - 生成工单草案。
   - 生成复盘报告。
   - 输出不确定性和人工确认点。

## Root Cause Ranking Formula

第一版可使用启发式评分：

```text
score = alarm_match * 0.30
      + sensor_correlation * 0.25
      + sop_match * 0.20
      + maintenance_similarity * 0.15
      + operator_note_match * 0.10
```

分数不是最终真相，只用于排序排查优先级。

## Required Output Sections

- Incident Summary
- Event Timeline
- Root Cause Candidates
- Evidence
- Immediate Actions
- Work Order Draft
- Postmortem Report
- Limitations
