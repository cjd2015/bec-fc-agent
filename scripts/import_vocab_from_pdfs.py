#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from pypdf import PdfReader
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set")

PDF_DIR = Path("/root/.openclaw/media/inbound")
PDFS = [
    {
        "path": PDF_DIR / "BEC中级高频词汇表---b56e6078-8543-4a81-a07d-b86dc96d8fb9.pdf",
        "level": "BEC Intermediate",
        "difficulty": "medium",
        "mode": "table",
    },
    {
        "path": PDF_DIR / "BEC中级高频词汇讲解---d7fa3630-6205-4b28-86e8-10322ba7a557.pdf",
        "level": "BEC Intermediate",
        "difficulty": "medium",
        "mode": "table",
    },
    {
        "path": PDF_DIR / "BEC国际金融词汇---25203997-806a-40ef-8680-17bf91d52d37.pdf",
        "level": "BEC Finance",
        "difficulty": "medium",
        "mode": "bilingual",
    },
    {
        "path": PDF_DIR / "BEC商务英语近义词辨析---9ba39a45-1245-420e-8831-d15bdd3273c9.pdf",
        "level": "BEC Synonyms",
        "difficulty": "medium",
        "mode": "text",
    },
]

LINE_PATTERN = re.compile(r"^([A-Za-z][A-Za-z \-/&']*[A-Za-z0-9])\s{2,}([A-Za-z. /()'-]+?)\s{2,}(.*)$")
BILINGUAL_PATTERN = re.compile(
    r"^(?P<zh>[\u4e00-\u9fff·（）()、/；;：:\s]+)(?P<en>[A-Za-z][A-Za-z0-9\s\-’'(),.&/]+)$"
)


def extract_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    texts: List[str] = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        texts.append(page_text)
    return "\n".join(texts)


def parse_bilingual_entries(raw_text: str) -> List[Dict[str, str]]:
    lines = [line.replace("\x00", "").strip() for line in raw_text.splitlines()]
    entries: List[Dict[str, str]] = []
    for line in lines:
        if not line:
            continue
        match = BILINGUAL_PATTERN.match(line)
        if not match:
            continue
        zh = match.group("zh").strip(" ：;；")
        en = match.group("en").strip()
        if not zh or not en:
            continue
        entries.append(
            {
                "word": en,
                "part_of_speech": "",
                "meaning_zh": zh,
            }
        )
    return entries


def parse_vocab_entries(raw_text: str) -> List[Dict[str, str]]:
    lines = [line.rstrip() for line in raw_text.splitlines()]
    entries: List[Dict[str, List[str]]] = []
    current: Dict[str, List[str]] | None = None
    for line in lines:
        line = line.replace("\x00", "").strip()
        if not line:
            continue
        if len(line) == 1 and line.isalpha():
            continue
        match = LINE_PATTERN.match(line)
        if match:
            if current:
                current["meaning"].append("")
                entries.append(current)
            word = match.group(1).strip()
            pos = match.group(2).strip()
            meaning = match.group(3).strip()
            current = {
                "word": word,
                "part_of_speech": pos,
                "meaning": [meaning] if meaning else [],
            }
        else:
            if current:
                current.setdefault("meaning", []).append(line)
    if current:
        entries.append(current)
    normalized: List[Dict[str, str]] = []
    for item in entries:
        meaning_text = " ".join(part.strip() for part in item.get("meaning", []) if part is not None).strip()
        if not meaning_text:
            continue
        normalized.append(
            {
                "word": item["word"].strip(),
                "part_of_speech": item["part_of_speech"].strip().rstrip('.'),
                "meaning_zh": meaning_text,
            }
        )
    return normalized


def upsert_entries(entries: List[Dict[str, str]], level: str, difficulty: str) -> int:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    inserted = 0
    with engine.begin() as conn:
        for entry in entries:
            word = entry["word"]
            part = entry["part_of_speech"]
            meaning = entry["meaning_zh"]
            existing = conn.execute(
                text("SELECT id FROM vocab_content WHERE word = :word AND part_of_speech = :pos LIMIT 1"),
                {"word": word, "pos": part},
            ).scalar()
            if existing:
                continue
            conn.execute(
                text(
                    """
                    INSERT INTO vocab_content (
                        word, phonetic, part_of_speech, meaning_zh,
                        business_example, collocation, level, difficulty,
                        review_status, publish_status
                    ) VALUES (
                        :word, NULL, :part, :meaning,
                        NULL, NULL, :level, :difficulty,
                        'approved', 'published'
                    )
                    """
                ),
                {
                    "word": word,
                    "part": part,
                    "meaning": meaning,
                    "level": level,
                    "difficulty": difficulty,
                },
            )
            inserted += 1
    return inserted


def main() -> None:
    total_inserted = 0
    for cfg in PDFS:
        pdf_path = cfg["path"]
        if not pdf_path.exists():
            print(f"[WARN] PDF not found: {pdf_path}")
            continue
        text = extract_text(pdf_path)
        mode = cfg.get("mode", "table")
        if mode == "bilingual":
            entries = parse_bilingual_entries(text)
        elif mode == "text":
            print(f"[INFO] skipping structured import for text-heavy PDF: {pdf_path.name}")
            continue
        else:
            entries = parse_vocab_entries(text)
        inserted = upsert_entries(entries, cfg["level"], cfg["difficulty"])
        print(f"Imported {inserted} entries from {pdf_path.name}")
        total_inserted += inserted
    print(f"Total inserted entries: {total_inserted}")


if __name__ == "__main__":
    main()
