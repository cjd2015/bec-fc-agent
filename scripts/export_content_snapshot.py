#!/usr/bin/env python3
"""Export question_content and scene_content records to SQL seed file."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable, List

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_FILE = BASE_DIR / "sql" / "seed_content_snapshot.sql"
load_dotenv(BASE_DIR / ".env")
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set in .env")

QUESTION_MODULES = ("level_test", "mock_exam")


def sql_literal(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    text_value = str(value).replace("'", "''")
    return f"'{text_value}'"


def json_literal(payload: Any) -> str:
    if payload is None:
        return "NULL"
    json_text = json.dumps(payload, ensure_ascii=False)
    json_text = json_text.replace("'", "''")
    return f"'{json_text}'::jsonb"


def chunked(iterable: Iterable[Any], size: int) -> Iterable[List[Any]]:
    chunk: List[Any] = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def export_question_content(engine) -> List[str]:
    statements: List[str] = []
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT module_type, question_type, stem, options_json,
                       correct_answer, explanation, level, difficulty,
                       review_status, publish_status
                FROM question_content
                WHERE module_type = ANY(:modules)
                ORDER BY module_type, id
                """
            ),
            {"modules": list(QUESTION_MODULES)},
        ).mappings().all()
    columns = (
        "module_type",
        "question_type",
        "stem",
        "options_json",
        "correct_answer",
        "explanation",
        "level",
        "difficulty",
        "review_status",
        "publish_status",
    )
    for batch in chunked(rows, 50):
        values_sql = []
        for row in batch:
            values_sql.append(
                "(" + ", ".join(
                    [
                        sql_literal(row["module_type"]),
                        sql_literal(row["question_type"]),
                        sql_literal(row["stem"]),
                        json_literal(row["options_json"]),
                        sql_literal(row["correct_answer"]),
                        sql_literal(row["explanation"]),
                        sql_literal(row["level"]),
                        sql_literal(row["difficulty"]),
                        sql_literal(row["review_status"]),
                        sql_literal(row["publish_status"]),
                    ]
                ) + ")"
            )
        stmt = (
            "INSERT INTO question_content (module_type, question_type, stem, options_json, "
            "correct_answer, explanation, level, difficulty, review_status, publish_status)\nVALUES\n    "
            + ",\n    ".join(values_sql)
            + "\nON CONFLICT DO NOTHING;"
        )
        statements.append(stmt)
    return statements


def export_scene_content(engine) -> List[str]:
    statements: List[str] = []
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT scene_name, scene_background, training_goal, user_role,
                       ai_role, prompt_template, recommended_expression,
                       level, difficulty, review_status, publish_status
                FROM scene_content
                ORDER BY id
                """
            )
        ).mappings().all()
    for batch in chunked(rows, 25):
        values_sql = []
        for row in batch:
            values_sql.append(
                "(" + ", ".join(
                    [
                        sql_literal(row["scene_name"]),
                        sql_literal(row["scene_background"]),
                        sql_literal(row["training_goal"]),
                        sql_literal(row["user_role"]),
                        sql_literal(row["ai_role"]),
                        sql_literal(row["prompt_template"]),
                        sql_literal(row["recommended_expression"]),
                        sql_literal(row["level"]),
                        sql_literal(row["difficulty"]),
                        sql_literal(row["review_status"]),
                        sql_literal(row["publish_status"]),
                    ]
                ) + ")"
            )
        stmt = (
            "INSERT INTO scene_content (scene_name, scene_background, training_goal, user_role, ai_role, "
            "prompt_template, recommended_expression, level, difficulty, review_status, publish_status)\nVALUES\n    "
            + ",\n    ".join(values_sql)
            + "\nON CONFLICT DO NOTHING;"
        )
        statements.append(stmt)
    return statements


def main() -> None:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    content: List[str] = ["BEGIN;"]
    content.extend(export_question_content(engine))
    content.extend(export_scene_content(engine))
    content.append("COMMIT;")

    OUTPUT_FILE.write_text("\n\n".join(content) + "\n", encoding="utf-8")
    print(f"Wrote snapshot to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
