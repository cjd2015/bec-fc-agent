#!/usr/bin/env python3
"""Seed pattern_content entries from YAML files."""
from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import yaml
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

BASE_DIR = Path(__file__).resolve().parents[1]
CONTENT_DIR = BASE_DIR / "content" / "patterns"
load_dotenv(BASE_DIR / ".env")
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set in .env")


@dataclass
class Pattern:
    pattern_text: str
    scene_type: Optional[str]
    function_type: Optional[str]
    example_text: Optional[str]
    slot_desc: Optional[str]
    level: Optional[str]
    difficulty: Optional[str]
    source_file: Path


def load_patterns(directory: Path) -> List[Pattern]:
    items: List[Pattern] = []
    for file_path in sorted(directory.glob("*.yaml")):
        data = yaml.safe_load(file_path.read_text(encoding="utf-8")) or {}
        for payload in data.get("patterns", []):
            text_value = (payload.get("pattern_text") or "").strip()
            if not text_value:
                raise ValueError(f"Missing pattern_text in {file_path}")
            items.append(
                Pattern(
                    pattern_text=text_value,
                    scene_type=(payload.get("scene_type") or None),
                    function_type=(payload.get("function_type") or None),
                    example_text=(payload.get("example_text") or None),
                    slot_desc=(payload.get("slot_desc") or None),
                    level=(payload.get("level") or None),
                    difficulty=(payload.get("difficulty") or None),
                    source_file=file_path,
                )
            )
    return items


def insert_patterns(engine: Engine, patterns: List[Pattern], dry_run: bool = False) -> int:
    inserted = 0
    with engine.begin() as conn:
        for pattern in patterns:
            exists = conn.execute(
                text("SELECT 1 FROM pattern_content WHERE pattern_text = :text LIMIT 1"),
                {"text": pattern.pattern_text},
            ).first()
            if exists:
                continue
            if dry_run:
                inserted += 1
                continue
            conn.execute(
                text(
                    """
                    INSERT INTO pattern_content (
                        pattern_text, scene_type, function_type,
                        example_text, slot_desc, level, difficulty,
                        review_status, publish_status
                    ) VALUES (
                        :pattern_text, :scene_type, :function_type,
                        :example_text, :slot_desc, :level, :difficulty,
                        'approved', 'published'
                    )
                    """
                ),
                {
                    "pattern_text": pattern.pattern_text,
                    "scene_type": pattern.scene_type,
                    "function_type": pattern.function_type,
                    "example_text": pattern.example_text,
                    "slot_desc": pattern.slot_desc,
                    "level": pattern.level,
                    "difficulty": pattern.difficulty,
                },
            )
            inserted += 1
    return inserted


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed pattern_content from YAML files")
    parser.add_argument("--dry-run", action="store_true", help="Parse files but skip inserts")
    args = parser.parse_args()

    if not CONTENT_DIR.exists():
        raise SystemExit(f"Pattern content directory not found: {CONTENT_DIR}")

    patterns = load_patterns(CONTENT_DIR)
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    inserted = insert_patterns(engine, patterns, dry_run=args.dry_run)

    if args.dry_run:
        print(f"Dry run complete. {inserted} pattern(s) would have been inserted.")
    else:
        print(f"Inserted {inserted} new pattern(s).")


if __name__ == "__main__":
    main()
