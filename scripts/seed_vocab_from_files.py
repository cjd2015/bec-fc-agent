#!/usr/bin/env python3
"""Seed vocab_content from YAML files generated in content/vocab."""
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
CONTENT_DIR = BASE_DIR / "content" / "vocab"
load_dotenv(BASE_DIR / ".env")
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set in .env")


@dataclass
class VocabEntry:
    word: str
    phonetic: Optional[str]
    part_of_speech: Optional[str]
    meaning_zh: str
    business_example: Optional[str]
    collocation: Optional[str]
    level: Optional[str]
    difficulty: Optional[str]
    source_file: Path


def load_entries(directory: Path) -> List[VocabEntry]:
    entries: List[VocabEntry] = []
    for file_path in sorted(directory.glob("*.yaml")):
        data = yaml.safe_load(file_path.read_text(encoding="utf-8")) or {}
        level = data.get("level")
        for payload in data.get("entries", []):
            word = (payload.get("word") or "").strip()
            meaning = (payload.get("meaning_zh") or "").strip()
            if not word or not meaning:
                continue
            entries.append(
                VocabEntry(
                    word=word,
                    phonetic=(payload.get("phonetic") or None),
                    part_of_speech=(payload.get("part_of_speech") or None),
                    meaning_zh=meaning,
                    business_example=(payload.get("business_example") or None),
                    collocation=(payload.get("collocation") or None),
                    level=payload.get("level") or level,
                    difficulty=payload.get("difficulty") or None,
                    source_file=file_path,
                )
            )
    return entries


def upsert_entries(engine: Engine, entries: List[VocabEntry], dry_run: bool = False) -> int:
    inserted = 0
    with engine.begin() as conn:
        for entry in entries:
            exists = conn.execute(
                text(
                    "SELECT 1 FROM vocab_content WHERE word = :word AND COALESCE(part_of_speech, '') = COALESCE(:pos, '') LIMIT 1"
                ),
                {"word": entry.word, "pos": entry.part_of_speech},
            ).first()
            if exists:
                continue
            if dry_run:
                inserted += 1
                continue
            conn.execute(
                text(
                    """
                    INSERT INTO vocab_content (
                        word, phonetic, part_of_speech, meaning_zh,
                        business_example, collocation, level, difficulty,
                        review_status, publish_status
                    ) VALUES (
                        :word, :phonetic, :part_of_speech, :meaning_zh,
                        :business_example, :collocation, :level, :difficulty,
                        'approved', 'published'
                    )
                    """
                ),
                {
                    "word": entry.word,
                    "phonetic": entry.phonetic,
                    "part_of_speech": entry.part_of_speech,
                    "meaning_zh": entry.meaning_zh,
                    "business_example": entry.business_example,
                    "collocation": entry.collocation,
                    "level": entry.level,
                    "difficulty": entry.difficulty,
                },
            )
            inserted += 1
    return inserted


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed vocab_content from YAML files")
    parser.add_argument("--dry-run", action="store_true", help="Parse files but skip inserts")
    args = parser.parse_args()

    if not CONTENT_DIR.exists():
        raise SystemExit(f"Vocab directory not found: {CONTENT_DIR}")

    entries = load_entries(CONTENT_DIR)
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    inserted = upsert_entries(engine, entries, dry_run=args.dry_run)

    if args.dry_run:
        print(f"Dry run complete. {inserted} vocab entry(ies) would have been inserted.")
    else:
        print(f"Inserted {inserted} new vocab entry(ies).")


if __name__ == "__main__":
    main()
