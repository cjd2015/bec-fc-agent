# Question Bank Content Directory

This directory contains the canonical source files for the BEC题库. Each YAML file describes a
set of multiple-choice questions for a specific learning module. The data is imported into the
`question_content` table via `scripts/seed_question_bank_from_files.py`.

## Structure

```
content/question_bank/
├── level_test/
│   ├── foundation_email.yaml
│   ├── meetings_alignment.yaml
│   ├── negotiation_strategy.yaml
│   └── executive_reporting.yaml
├── mock_exam/
│   ├── customer_communication.yaml
│   ├── project_delivery.yaml
│   ├── strategy_alignment.yaml
│   └── risk_finance.yaml
└── README.md
```

Each YAML file uses the following schema:

```yaml
module: level_test | mock_exam
source: "short free-text attribution"
version: 1
questions:
  - stem: "Question prompt"
    level: "BEC Preliminary | BEC Vantage | BEC Higher"
    difficulty: "easy | medium | hard"
    tags: [email, etiquette]
    options:
      - "Option A text"
      - "Option B text"
      - ...
    answer: "Exact text of the correct option"
    explanation: "Short rationale"
```

Notes:
- `options` may include plain strings or dictionaries with `label`/`value`. During import they are
  normalized into `[{"value": "...", "label": "..."}]` before insertion.
- `tags` are currently metadata only (useful for future filtering or analytics) and are not stored
  in the relational schema.
- Every question is imported as `question_type = 'single_choice'`, `review_status = 'approved'`,
  `publish_status = 'published'`.

## Importing Into PostgreSQL

Run the helper script from the project root:

```bash
python3 scripts/seed_question_bank_from_files.py          # import all modules
python3 scripts/seed_question_bank_from_files.py --module level_test
python3 scripts/seed_question_bank_from_files.py --dry-run
```

The script prevents duplicate inserts by checking `module_type + stem`. After importing you can
verify counts with:

```bash
python3 - <<'PY'
from sqlalchemy import create_engine, text
engine = create_engine("$DATABASE_URL")
with engine.connect() as conn:
    for module in ("level_test", "mock_exam"):
        total = conn.execute(text("SELECT COUNT(*) FROM question_content WHERE module_type=:m"), {"m": module}).scalar()
        print(module, total)
PY
```

Keeping the question source files under version control ensures we never lose authored content and
can track edits through pull requests. Add new YAML files (or append to existing ones) when more
题目 are needed, then rerun the seed script.
