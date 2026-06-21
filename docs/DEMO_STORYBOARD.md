# Demo Storyboard

## Demo Title

ForgePulse: Battery Coating Line Maintenance Agent

## One-sentence Opening

新能源电池产线一旦出现温控和张力耦合异常，排障往往依赖资深工程师经验；ForgePulse 将报警、传感器、SOP 和维修记录整合成可执行的诊断闭环。

## Demo Flow

1. 打开工作台。
2. 选择案例：`coating_line_dryer_tension_001`。
3. 展示输入资产：
   - sensor_readings.csv
   - alarms.csv
   - sop_dryer_tension.md
   - maintenance_records.md
4. 点击 Diagnose。
5. 展示异常时间线：
   - 10:12 张力开始振荡。
   - 10:16 干燥 2 区温度升高。
   - 10:18 触发温控偏差报警。
   - 10:22 膜厚开始偏离目标区间。
6. 展示根因候选：
   - 干燥 2 区温控回路不稳定。
   - 张力闭环响应滞后。
   - 风机频率波动导致局部热场不均。
7. 展示证据链。
8. 生成维修工单。
9. 生成复盘报告。
10. 说明价值：
    - 缩短排障路径。
    - 降低重复故障沟通成本。
    - 沉淀设备知识。
    - 支持厂内本地化部署。

## Visual Requirements

- 不做营销首页。
- 第一屏就是工程师工作台。
- 时间线和证据链必须明显。
- 工单和报告要像真实工作产物。
