#!/usr/bin/env python3
"""Lightweight validation for question_content / scene_content / pattern_content."""
from __future__ import annotations

import os
import random
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set in .env")

MODULES = ("level_test", "mock_exam")


def assert_condition(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_questions(conn) -> None:
    for module in MODULES:
        total = conn.execute(
            text("SELECT count(*) FROM question_content WHERE module_type = :m"),
            {"m": module},
        ).scalar()
        assert_condition(total and total >= 20, f"Question count too low for {module}: {total}")
        sample = conn.execute(
            text(
                """
                SELECT stem, options_json
                FROM question_content
                WHERE module_type = :m
                ORDER BY random()
                LIMIT 5
                """
            ),
            {"m": module},
        ).mappings().all()
        for row in sample:
            options = row["options_json"] or []
            assert_condition(len(options) >= 2, f"Question missing options: {row['stem'][:50]}")


def validate_scenes(conn) -> None:
    total = conn.execute(text("SELECT count(*) FROM scene_content")).scalar()
    assert_condition(total and total >= 10, f"Scene count too low: {total}")
    sample = conn.execute(
        text("SELECT scene_name, prompt_template FROM scene_content ORDER BY random() LIMIT 3")
    ).mappings().all()
    for row in sample:
        assert_condition(row["prompt_template"], f"Scene missing prompt: {row['scene_name']}")


def validate_patterns(conn) -> None:
    total = conn.execute(text("SELECT count(*) FROM pattern_content")).scalar()
    assert_condition(total and total >= 30, f"Pattern count too low: {total}")
    sample = conn.execute(
        text(
            "SELECT pattern_text, example_text FROM pattern_content ORDER BY random() LIMIT 5"
        )
    ).mappings().all()
    for row in sample:
        assert_condition(row["example_text"], f"Pattern missing example: {row['pattern_text']}")


def main() -> None:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with engine.connect() as conn:
        validate_questions(conn)
        validate_scenes(conn)
        validate_patterns(conn)
    print("Question bank validation passed.")


if __name__ == "__main__":
    main()
