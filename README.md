# TechFest Pakistani-context NER

Stage 1 provides annotation configuration and validation only. No training,
model downloads, scraping, or benchmark claims are included.

## Project structure

```text
config/labels.py             # 20 entity types, 41 BIO labels, ID mappings
scripts/validate_data.py     # Standard-library-only validator
data/synthetic_sample.jsonl # Tiny fictional annotation examples
docs/annotation_format.md   # Annotation contract and conventions
.venv/                      # Existing local environment (preserved)
```

## Run validation in PowerShell

From the project root:

```powershell
.\.venv\Scripts\python.exe scripts/validate_data.pydata/synthetic_sample.jsonl
```

Replace the final path to check your own dataset. Activation is optional when
using the interpreter directly. No additional packages are required.
A valid file exits with status 0; invalid input exits with status 1 and prints
line-specific errors. Inspect `$LASTEXITCODE` after running the command.

Checks include strict JSON objects, required fields, value types, nonempty
arrays/tokens, aligned token/tag counts, known labels, valid BIO transitions,
duplicate IDs and duplicate token sequences (even with different tags).
Empty files, blank lines, duplicate JSON keys, and nonstandard JSON constants
are rejected. Extra metadata fields are allowed.

Read [the annotation guide](docs/annotation_format.md) before creating data.
The sample is synthetic and is only a format demonstration, not evaluation data.
The validator cannot verify annotation meaning, detect real personal data, or
measure model performance. Keep phone and ID examples synthetic.
