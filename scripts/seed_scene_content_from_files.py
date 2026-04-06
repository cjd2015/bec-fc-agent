#!/usr/bin/env python3
"""Import scene training definitions from YAML files into scene_content."""
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
CONTENT_DIR = BASE_DIR / "content" / "scene_training"
load_dotenv(BASE_DIR / ".env")
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set in .env")


@dataclass
class Scene:
    scene_name: str
    scene_background: str
    training_goal: str
    user_role: Optional[str]
    ai_role: Optional[str]
    prompt_template: str
    recommended_expression: Optional[str]
    level: Optional[str]
    difficulty: Optional[str]
    source_file: Path


def load_scenes(directory: Path) -> List[Scene]:
    scenes: List[Scene] = []
    for file_path in sorted(directory.glob("*.yaml")):
        data = yaml.safe_load(file_path.read_text(encoding="utf-8")) or {}
        for payload in data.get("scenes", []):
            scene_name = (payload.get("scene_name") or "").strip()
            if not scene_name:
                raise ValueError(f"Missing scene_name in {file_path}")
            scenes.append(
                Scene(
                    scene_name=scene_name,
                    scene_background=(payload.get("scene_background") or "").strip(),
                    training_goal=(payload.get("training_goal") or "").strip(),
                    user_role=(payload.get("user_role") or None),
                    ai_role=(payload.get("ai_role") or None),
                    prompt_template=(payload.get("prompt_template") or "").strip(),
                    recommended_expression=(payload.get("recommended_expression") or None),
                    level=(payload.get("level") or None),
                    difficulty=(payload.get("difficulty") or None),
                    source_file=file_path,
                )
            )
    return scenes


def insert_scenes(engine: Engine, scenes: List[Scene], dry_run: bool = False) -> int:
    inserted = 0
    with engine.begin() as conn:
        for scene in scenes:
            exists = conn.execute(
                text(
                    """
                    SELECT 1 FROM scene_content
                    WHERE scene_name = :scene_name
                    LIMIT 1
                    """
                ),
                {"scene_name": scene.scene_name},
            ).first()
            if exists:
                continue
            if dry_run:
                inserted += 1
                continue
            conn.execute(
                text(
                    """
                    INSERT INTO scene_content (
                        scene_name, scene_background, training_goal,
                        user_role, ai_role, prompt_template, recommended_expression,
                        level, difficulty, review_status, publish_status
                    ) VALUES (
                        :scene_name, :scene_background, :training_goal,
                        :user_role, :ai_role, :prompt_template, :recommended_expression,
                        :level, :difficulty, 'approved', 'published'
                    )
                    """
                ),
                {
                    "scene_name": scene.scene_name,
                    "scene_background": scene.scene_background,
                    "training_goal": scene.training_goal,
                    "user_role": scene.user_role,
                    "ai_role": scene.ai_role,
                    "prompt_template": scene.prompt_template,
                    "recommended_expression": scene.recommended_expression,
                    "level": scene.level,
                    "difficulty": scene.difficulty,
                },
            )
            inserted += 1
    return inserted


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed scene_content from YAML files")
    parser.add_argument("--dry-run", action="store_true", help="Parse files but do not insert")
    args = parser.parse_args()

    if not CONTENT_DIR.exists():
        raise SystemExit(f"Scene content directory not found: {CONTENT_DIR}")

    scenes = load_scenes(CONTENT_DIR)
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    inserted = insert_scenes(engine, scenes, dry_run=args.dry_run)

    if args.dry_run:
        print(f"Dry run complete. {inserted} scene(s) would have been inserted.")
    else:
        print(f"Inserted {inserted} new scene(s).")


if __name__ == "__main__":
    main()
