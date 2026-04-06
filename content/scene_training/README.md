# Scene Training Content

Structured definitions for对话训练场景。每个 YAML 文件代表一个主题，包含多个 `scenes` 条目：

```yaml
module: scene_training
source: "free-text attribution"
version: 1
scenes:
  - scene_name: "Quarterly Business Review"
    scene_background: "Context"
    training_goal: "重点练习能力"
    user_role: "Learner身份"
    ai_role: "AI 承担角色"
    prompt_template: |
      多轮提示，告诉 AI 如何回应
    recommended_expression: |
      "短语1"; "短语2"
    level: "BEC Preliminary | BEC Vantage | BEC Higher"
    difficulty: "easy | medium | hard"
```

导入脚本：

```bash
python3 scripts/seed_scene_content_from_files.py
python3 scripts/seed_scene_content_from_files.py --dry-run
```

脚本会跳过相同 `scene_name` 的重复记录，并自动将 `review_status/publish_status` 设为 `approved/published`。
