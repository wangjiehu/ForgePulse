# Data Contracts

ForgePulse 的数据必须先结构化，再交给 Agent 推理。

## Case Manifest

位置：

```text
data/samples/<case_id>/case_manifest.json
```

关键字段：

- `case_id`
- `title`
- `industry`
- `line`
- `station`
- `incident_window`
- `files`
- `expected_outputs`

## Sensor CSV

必需列：

- `timestamp`
- `dryer_zone_1_temp_c`
- `dryer_zone_2_temp_c`
- `web_tension_n`
- `line_speed_m_min`
- `fan_frequency_hz`
- `drive_current_a`
- `thickness_um`

## Alarm CSV

必需列：

- `timestamp`
- `alarm_code`
- `severity`
- `message`
- `status`

## Evidence Object

```json
{
  "id": "EV-001",
  "source": "sensor_csv",
  "timestamp": "2026-06-10T10:18:00+08:00",
  "summary": "dryer_zone_2_temp_c rose above upper control band",
  "value": "96.8 C",
  "field": "dryer_zone_2_temp_c"
}
```

## Diagnosis Object

```json
{
  "candidate_id": "RC-001",
  "title": "Dryer zone 2 temperature control loop instability",
  "confidence": 0.78,
  "priority": "high",
  "evidence_ids": ["EV-001", "EV-004"],
  "recommended_actions": ["Check temperature controller output", "Inspect heater relay and sensor wiring"]
}
```
