# AI Build Protocol

ForgePulse 按“AI 可以持续接手完成”的方式组织。任何后续 AI Agent 开发时都应遵守本协议。

## Principles

1. Spec first: 先更新契约、样例和评测，再改实现。
2. Evidence first: 诊断结论必须引用输入数据或文档证据。
3. Deterministic baseline first: 先保证无模型 Token 的基础 demo 可运行。
4. Synthetic public data only: 公开仓库只放合成数据或脱敏数据。
5. Narrow scenario first: 先把一个工段跑通，再扩展更多场景。

## Required Implementation Order

1. Data loader
2. Sensor anomaly analyzer
3. Alarm parser
4. SOP and maintenance retriever
5. Diagnosis composer
6. Work-order generator
7. Report generator
8. Frontend dashboard
9. LLM provider adapter
10. Ascend/NPU integration notes or adapter

## Output Rules

Agent 输出必须分为：

- `facts`: 直接来自数据的事实。
- `evidence`: 可定位证据。
- `hypotheses`: 根因候选。
- `actions`: 建议动作。
- `limits`: 不确定性和需要人工确认的点。

禁止：

- 编造不存在的传感器数据。
- 编造不存在的 SOP 条款。
- 给出没有证据的确定性结论。
- 声称可以替代现场安全责任人。

## Human Review Points

即使由 AI 完成，以下内容仍需要人工最终确认：

- 真实工厂接入前的安全流程。
- 设备操作和停机建议。
- 商业宣传中的量化收益。
- 任何真实数据的公开发布。
