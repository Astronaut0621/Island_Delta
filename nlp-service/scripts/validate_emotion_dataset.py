import argparse
import csv
from collections import Counter
from pathlib import Path


EXPECTED_LABELS = [
    "lonely",
    "anxious",
    "stressed",
    "tired",
    "sad",
    "calm",
    "healed",
    "secure",
    "happy",
    "hopeful",
]

EXPECTED_SOURCES = {"manual", "ai_generated"}
REQUIRED_FIELDS = ["id", "text", "emotion_type", "source"]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != REQUIRED_FIELDS:
            raise ValueError(f"CSV fields must be {REQUIRED_FIELDS}, got {reader.fieldnames}")
        return list(reader)


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    ids: list[int] = []
    texts: list[str] = []

    for index, row in enumerate(rows, start=2):
        try:
            ids.append(int(row["id"]))
        except ValueError:
            errors.append(f"line {index}: id must be an integer")

        text = row["text"].strip()
        if not text:
            errors.append(f"line {index}: text is empty")
        texts.append(text)

        if row["emotion_type"] not in EXPECTED_LABELS:
            errors.append(f"line {index}: unknown emotion_type {row['emotion_type']!r}")

        if row["source"] not in EXPECTED_SOURCES:
            errors.append(f"line {index}: unknown source {row['source']!r}")

    duplicate_ids = [item for item, count in Counter(ids).items() if count > 1]
    if duplicate_ids:
        errors.append(f"duplicate ids: {duplicate_ids[:10]}")

    duplicate_texts = [item for item, count in Counter(texts).items() if count > 1]
    if duplicate_texts:
        errors.append(f"duplicate texts: {duplicate_texts[:5]}")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    args = parser.parse_args()

    rows = read_rows(args.dataset)
    errors = validate_rows(rows)

    print(f"rows: {len(rows)}")
    print("emotion_counts:")
    emotion_counts = Counter(row["emotion_type"] for row in rows)
    for label in EXPECTED_LABELS:
        print(f"  {label}: {emotion_counts[label]}")

    print("source_counts:")
    source_counts = Counter(row["source"] for row in rows)
    for source, count in sorted(source_counts.items()):
        print(f"  {source}: {count}")

    if errors:
        print("errors:")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)

    print("status: ok")


if __name__ == "__main__":
    main()
