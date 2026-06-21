# Evaluation Plan

ForgePulse 的评测目标是判断 Agent 是否真正完成行业诊断，而不是判断回答是否好看。

## Evaluation Dimensions

### 1. Scenario Fit

- 是否明确绑定电池制造产线。
- 是否解决设备异常诊断问题。
- 是否输出工程师可执行结果。

### 2. Evidence Grounding

- 根因候选是否引用传感器、报警或文档证据。
- 是否能定位证据来源。
- 是否避免无证据断言。

### 3. Diagnostic Quality

- 是否识别关键异常窗口。
- 是否给出合理排查顺序。
- 是否说明不确定性。

### 4. Actionability

- 建议是否能转化为维修工单。
- 是否区分立即检查和停机检查。
- 是否包含安全注意事项。

### 5. Demo Reliability

- 样例案例是否可重复运行。
- 无模型 Token 时是否仍有基础输出。
- UI 是否稳定展示关键结果。

## Golden Cases

评测包含五个 golden cases：

```text
coating_line_dryer_tension_001       -> confirmed
coating_line_airflow_002             -> confirmed
coating_line_drive_resistance_003    -> confirmed
coating_line_incomplete_evidence_004 -> insufficient_evidence
coating_line_conflicting_evidence_005 -> conflicting_evidence
```

每个案例目录内的 `golden_expectations.json` 是可执行真值源；`evaluation/golden_cases.json` 仅用于人工快速审阅案例覆盖。

## Pass Criteria

基础通过：

- 找到异常窗口。
- 根因候选包含温控回路异常。
- 至少引用 3 条证据。
- 输出工单草案。
- 输出限制说明。
- 证据不足或冲突时不得输出已确认结论。
- 所有根因、动作和证据图引用必须指向真实对象。
- 相同输入的输出必须确定一致。

优秀：

- 能解释温控和张力波动如何共同影响膜厚。
- 能给出停机/不停机排查顺序。
- 能把维修记录中的相似案例纳入证据。
- 反事实移除关键报警后，相关根因分数必须下降。
- 评测不能把 golden 标签泄漏给诊断引擎。
