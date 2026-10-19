"""Validate token-level BIO JSONL without third-party dependencies."""

import argparse
import json
from pathlib import Path
import sys

# Allow running this file directly from any working directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.labels import BIO_LABELS


def validate_record(record):
    """Return all structural and BIO errors found in a single JSON record."""
    errors = []
    if not isinstance(record, dict):
        return ["record must be a JSON object"]
    for field in ("id", "tokens", "ner_tags"):
        if field not in record:
            errors.append(f"missing required field: {field}")
    if "id" in record and (
        not isinstance(record["id"], str) or not record["id"].strip()
    ):
        errors.append("id must be a nonempty string")
    tokens = record.get("tokens")
    tags = record.get("ner_tags")
    if "tokens" in record and (
        not isinstance(tokens, list) or not tokens
        or any(not isinstance(t, str) or not t.strip() for t in tokens)
    ):
        errors.append("tokens must be a nonempty list of nonempty strings")
    if "ner_tags" in record and (
        not isinstance(tags, list) or not tags
        or any(not isinstance(t, str) for t in tags)
    ):
        errors.append("ner_tags must be a nonempty list of strings")
    if isinstance(tokens, list) and isinstance(tags, list) and len(tokens) != len(tags):
        errors.append("tokens and ner_tags must have equal lengths")
    if isinstance(tags, list):
        previous = "O"
        for index, tag in enumerate(tags):
            if not isinstance(tag, str) or tag not in BIO_LABELS:
                errors.append(f"token {index}: unknown label {tag!r}")
                previous = "O"
                continue
            if tag.startswith("I-") and previous not in (
                "B-" + tag[2:], "I-" + tag[2:]
            ):
                errors.append(f"token {index}: malformed BIO transition {previous} -> {tag}")
            previous = tag
    return errors


def reject_constant(value):
    raise ValueError(f"nonstandard JSON constant: {value}")


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def validate_file(path):
    """Return (record count, diagnostics); duplicate checks span the file."""
    diagnostics = []
    seen_ids, seen_tokens = {}, {}
    count = 0
    try:
        with path.open(encoding="utf-8") as source:
            for line_number, line in enumerate(source, 1):
                prefix = f"line {line_number}"
                if not line.strip():
                    diagnostics.append(f"{prefix}: blank lines are not allowed")
                    continue
                try:
                    record = json.loads(line, parse_constant=reject_constant,
                                        object_pairs_hook=unique_keys)
                except ValueError as exc:
                    diagnostics.append(f"{prefix}: invalid JSON: {exc}")
                    continue
                count += 1
                diagnostics.extend(f"{prefix}: {error}" for error in validate_record(record))
                if not isinstance(record, dict):
                    continue
                record_id = record.get("id")
                if isinstance(record_id, str) and record_id.strip():
                    if record_id in seen_ids:
                        diagnostics.append(f"{prefix}: duplicate id (first on line {seen_ids[record_id]})")
                    else:
                        seen_ids[record_id] = line_number
                tokens = record.get("tokens")
                if isinstance(tokens, list) and tokens and all(isinstance(t, str) for t in tokens):
                    key = tuple(tokens)
                    if key in seen_tokens:
                        diagnostics.append(f"{prefix}: duplicate example tokens (first on line {seen_tokens[key]})")
                    else:
                        seen_tokens[key] = line_number
    except (OSError, UnicodeError) as exc:
        diagnostics.append(f"cannot read UTF-8 input: {exc}")
    if count == 0:
        diagnostics.append("file contains no JSON records")
    return count, diagnostics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="UTF-8 JSONL annotation file")
    args = parser.parse_args()
    count, errors = validate_file(args.path)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAIL: {count} records checked; {len(errors)} errors.")
        return 1
    print(f"PASS: {count} records; format, required fields, label vocabulary, "
          "BIO sequences, alignment, and duplicate checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
