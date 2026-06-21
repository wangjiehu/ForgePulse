# Ascend Integration Route

ForgePulse 第一版不把 NPU 作为运行前提，但架构要能自然解释 Ascend 的价值。

## Why Ascend Fits

工业产线场景关注：

- 数据不出厂。
- 低延迟报警摘要。
- 边缘节点部署。
- 批量日志和文档处理。
- 模型推理成本可控。

这些需求与 Ascend/NPU 的本地化推理路线匹配。

## Integration Stages

### Stage 1: Provider Abstraction

后端只依赖 `ModelProvider` 接口，不把具体模型写死。

已实现并验证：

- 默认 `FORGEPULSE_MODEL_PROVIDER=offline`。
- 可选 OpenAI-compatible 网关。
- 模型仅能增强摘要措辞。
- 未知 Evidence ID 会触发回退。
- 模型无法改变诊断状态、根因、置信度、动作或工单。

### Stage 2: Local Model Gateway

将 LLM 调用切换到厂内部署服务或 CodingPlan 模型服务。

### Stage 3: Ascend Skill Experiments

记录使用昇腾 NPU 模型适配/调优 skill 的过程：

```text
/plugin marketplace add https://gitcode.com/gmq123/ascend-model-agent-plugin
/plugin install ascend-model-agent-plugin@ascend-model-agent-plugin
```

只有在真实安装、执行并保留可复现日志后，才能把该阶段标记为完成。

### Stage 4: Edge Deployment

将 ForgePulse 后端部署到厂内边缘节点，连接只读数据源。

## What Not To Claim

- 不声称已完成真实工厂部署，除非有证据。
- 不声称 Agent 能替代安全人员。
- 不声称模型单独完成设备控制。

## Current Verified Status

- Provider 抽象和离线回退：已验证。
- 兼容网关的约束与 Evidence ID 校验：已通过单元测试。
- 昇腾硬件推理：未验证。
- NPU 性能、精度和能耗数据：无，不作声明。
