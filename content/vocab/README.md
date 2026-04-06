# Vocab Content Source

所有词汇内容分级写在 `content/vocab/*.yaml` 中，由 `scripts/export_vocab_to_files.py` 生成，也可手动编辑。

每个文件示例：

```yaml
module: vocab
level: BEC Vantage
count: 250
entries:
  - word: "agenda"
    phonetic: "/əˈdʒendə/"
    part_of_speech: "noun"
    meaning_zh: "议程"
    business_example: "Let us begin with the first item on today's agenda."
    collocation: "meeting agenda"
    level: "BEC Preliminary"
    difficulty: "easy"
```

导入：

```bash
python3 scripts/seed_vocab_from_files.py
python3 scripts/seed_vocab_from_files.py --dry-run
```

导出（从数据库 → YAML）：

```bash
python3 scripts/export_vocab_to_files.py
```

> 约定：字典文件是词汇的权威来源。任何变更先改 YAML，再运行 seed 脚本写入数据库。`export_*` 仅用于生成初始文件或做快照，避免直接在数据库里手写数据。