# Pattern Content Library

结构化维护商务句型模板。字段说明：

```yaml
module: pattern
source: "attribution"
version: 1
patterns:
  - pattern_text: "If I understand correctly, ..."
    scene_type: "meeting"
    function_type: "confirmation"
    example_text: "If I understand correctly, the shipment leaves on Monday."
    slot_desc: "简述可变 slot"
    level: "BEC Preliminary"
    difficulty: "easy"
```

使用脚本导入：

```bash
python3 scripts/seed_patterns_from_files.py
python3 scripts/seed_patterns_from_files.py --dry-run
```

脚本会根据 `pattern_text` 去重，并自动写入 `pattern_content`（状态设为 `approved/published`）。
