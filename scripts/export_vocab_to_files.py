#!/usr/bin/env python3
"""Export vocab_content entries into YAML files grouped by level."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

import yaml
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "content" / "vocab"
load_dotenv(BASE_DIR / ".env")
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set in .env")


def slugify(level: str) -> str:
    return level.lower().replace(" ", "_")


def fetch_vocab() -> Dict[str, List[dict]]:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    data: Dict[str, List[dict]] = {}
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT word, phonetic, part_of_speech, meaning_zh,
                       business_example, collocation, level, difficulty
                FROM vocab_content
                ORDER BY level, word
                """
            )
        ).mappings().all()
    for row in rows:
        level = row["level"] or "Unknown"
        data.setdefault(level, []).append(dict(row))
    return data


def write_yaml(level: str, entries: List[dict]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "module": "vocab",
        "level": level,
        "count": len(entries),
        "entries": entries,
    }
    path = OUTPUT_DIR / f"{slugify(level)}.yaml"
    path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def main() -> None:
    vocab_by_level = fetch_vocab()
    if not vocab_by_level:
        raise SystemExit("No vocab entries found")
    written = []
    for level, entries in sorted(vocab_by_level.items()):
        written.append(write_yaml(level, entries))
    print("Exported", len(written), "YAML file(s):")
    for path in written:
        print(" -", path.relative_to(BASE_DIR))


if __name__ == "__main__":
    main()
