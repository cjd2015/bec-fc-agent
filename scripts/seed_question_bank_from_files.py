#!/usr/bin/env python3
"""Load structured question content files and insert into question_content."""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

BASE_DIR = Path(__file__).resolve().parents[1]
CONTENT_ROOT = BASE_DIR / "content" / "question_bank"
load_dotenv(BASE_DIR / ".env")
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set in .env")

SUPPORTED_MODULES = {"level_test", "mock_exam"}


@dataclass
class Question:
    module: str
    stem: str
    options: List[Dict[str, Any]]
    answer: str
    explanation: str
    level: Optional[str]
    difficulty: Optional[str]
    source_file: Path
    tags: List[str]

    def to_record(self) -> Dict[str, Any]:
        return {
            "module_type": self.module,
            "stem": self.stem.strip(),
            "options_json": json.dumps(self.options, ensure_ascii=False),
            "correct_answer": self.answer.strip(),
            "explanation": self.explanation.strip(),
            "level": self.level,
            "difficulty": self.difficulty,
        }


def normalize_options(raw_options: Iterable[Any], source: Path) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for idx, item in enumerate(raw_options):
        if isinstance(item, str):
            normalized.append({"value": item.strip(), "label": item.strip()})
        elif isinstance(item, dict):
            label = item.get("label") or item.get("text") or item.get("value")
            value = item.get("value") or item.get("text") or label or f"option_{idx+1}"
            normalized.append({"value": str(value).strip(), "label": str(label).strip()})
        else:
            raise ValueError(f"Unsupported option type in {source}: {item!r}")
    if not normalized:
        raise ValueError(f"No options provided in {source}")
    return normalized


def extract_questions(module: str, directory: Path) -> List[Question]:
    records: List[Question] = []
    for file_path in sorted(directory.glob("*.yaml")):
        data = yaml.safe_load(file_path.read_text(encoding="utf-8")) or {}
        questions = data.get("questions") or []
        for entry in questions:
            stem = (entry.get("stem") or "").strip()
            if not stem:
                raise ValueError(f"Missing stem in {file_path}")
            options = normalize_options(entry.get("options") or [], file_path)
            answer = entry.get("answer")
            if not answer:
                raise ValueError(f"Missing answer for question '{stem}' in {file_path}")
            explanation = entry.get("explanation") or ""
            level = entry.get("level")
            difficulty = entry.get("difficulty")
            tags = entry.get("tags") or []
            # Accept answers specified as labels or values; we store the label text
            matched_answer = None
            answer_text = str(answer).strip()
            for option in options:
                if answer_text.lower() in {option["value"].lower(), option["label"].lower()}:
                    matched_answer = option["label"]
                    break
            if not matched_answer:
                # allow direct text if not matching any label exactly
                matched_answer = answer_text
            records.append(
                Question(
                    module=module,
                    stem=stem,
                    options=options,
                    answer=matched_answer,
                    explanation=explanation,
                    level=level,
                    difficulty=difficulty,
                    source_file=file_path,
                    tags=tags,
                )
            )
    return records


def upsert_questions(engine: Engine, questions: List[Question], dry_run: bool = False) -> int:
    inserted = 0
    with engine.begin() as conn:
        for question in questions:
            exists = conn.execute(
                text(
                    """
                    SELECT 1 FROM question_content
                    WHERE module_type = :module AND stem = :stem
                    LIMIT 1
                    """
                ),
                {"module": question.module, "stem": question.stem},
            ).first()
            if exists:
                continue
            if dry_run:
                inserted += 1
                continue
            conn.execute(
                text(
                    """
                    INSERT INTO question_content (
                        module_type, question_type, stem, options_json,
                        correct_answer, explanation, level, difficulty,
                        review_status, publish_status
                    ) VALUES (
                        :module_type, 'single_choice', :stem, :options_json,
                        :correct_answer, :explanation, :level, :difficulty,
                        'approved', 'published'
                    )
                    """
                ),
                question.to_record(),
            )
            inserted += 1
    return inserted


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed question bank from structured content files")
    parser.add_argument(
        "--module",
        choices=sorted(SUPPORTED_MODULES),
        default=None,
        help="Only load a specific module",
    )
    parser.add_argument("--dry-run", action="store_true", help="Parse files but do not write to DB")
    args = parser.parse_args()

    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    modules = [args.module] if args.module else sorted(SUPPORTED_MODULES)

    total_inserted = 0
    for module in modules:
        directory = CONTENT_ROOT / module
        if not directory.exists():
            print(f"[warn] directory not found for module {module}: {directory}")
            continue
        questions = extract_questions(module, directory)
        inserted = upsert_questions(engine, questions, dry_run=args.dry_run)
        total_inserted += inserted
        print(f"Module {module}: prepared {len(questions)} question(s), inserted {inserted} new record(s)")

    if args.dry_run:
        print(f"Dry run complete. {total_inserted} record(s) would have been inserted.")
    else:
        print(f"Done. Inserted {total_inserted} new question(s).")


if __name__ == "__main__":
    main()
