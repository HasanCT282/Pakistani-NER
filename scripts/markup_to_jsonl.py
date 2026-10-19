"""Convert readable [text|TYPE] markup to the project's BIO JSONL format."""
import argparse
import json
from pathlib import Path
import re
import sys
import unicodedata

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.labels import ENTITY_TYPES
from scripts.validate_data import validate_record


def word_character(char):
    # Unicode letters/numbers and combining marks keep Urdu words together.
    return unicodedata.category(char)[0] in 'LNM'


def token_offsets(text):
    """Yield (token, start, end); punctuation is internal only between words."""
    i = 0
    while i < len(text):
        if text[i].isspace():
            i += 1
            continue
        start = i
        if word_character(text[i]):
            i += 1
            while i < len(text):
                if word_character(text[i]):
                    i += 1
                elif (text[i] in "-'.:,/" and i + 1 < len(text)
                      and word_character(text[i + 1])):
                    i += 2
                else:
                    break
        else:
            i += 1
        yield text[start:i], start, i


def parse_markup(markup):
    # Remove markup while recording character offsets in the original sentence.
    parts, spans = [], []
    cursor = length = 0
    while cursor < len(markup):
        char = markup[cursor]
        if char in ']|':
            raise ValueError('unexpected closing bracket or pipe')
        if char != '[':
            parts.append(char)
            length += 1
            cursor += 1
            continue
        end = markup.find(']', cursor + 1)
        if end < 0:
            raise ValueError('unclosed entity bracket')
        body = markup[cursor + 1:end]
        if '[' in body or body.count('|') != 1:
            raise ValueError('malformed or nested entity; expected [text|TYPE]')
        text, kind = body.split('|')
        if not text.strip() or text != text.strip():
            raise ValueError('empty entity span or whitespace at span edges')
        if kind not in ENTITY_TYPES:
            raise ValueError(f'unknown entity type: {kind!r}')
        parts.append(text)
        spans.append((length, length + len(text), kind))
        length += len(text)
        cursor = end + 1
    plain = ''.join(parts)
    offsets = list(token_offsets(plain))
    if not offsets:
        raise ValueError('sentence has no tokens')
    tags = ['O'] * len(offsets)
    for start, end, kind in spans:
        indexes = [i for i, (_, a, b) in enumerate(offsets) if a < end and b > start]
        if not indexes or offsets[indexes[0]][1] != start or offsets[indexes[-1]][2] != end:
            raise ValueError('entity boundary splits a token')
        for position, index in enumerate(indexes):
            tags[index] = ('B-' if position == 0 else 'I-') + kind
    return [token for token, _, _ in offsets], tags


def convert(source):
    records, seen_ids, seen_tokens = [], set(), set()
    for line_number, line in enumerate(source.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        try:
            fields = line.split(' @@ ')
            if len(fields) != 3:
                raise ValueError('expected lang @@ group @@ marked sentence')
            lang, group, markup = fields
            if lang not in ('en', 'ur', 'ru'):
                raise ValueError('language must be en, ur or ru')
            if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*\d', group):
                raise ValueError('group must start with a letter and end in digits')
            tokens, tags = parse_markup(markup)
            record = dict(id=f'pilot-{group}-{lang}', tokens=tokens, ner_tags=tags,
                          lang=lang, group=group, source='codex-authored-pilot', reviewed=False)
            errors = validate_record(record)
            if errors:
                raise ValueError('; '.join(errors))
            if record['id'] in seen_ids:
                raise ValueError('duplicate group/language combination')
            if tuple(tokens) in seen_tokens:
                raise ValueError('duplicate token sequence')
            seen_ids.add(record['id'])
            seen_tokens.add(tuple(tokens))
            records.append(record)
        except ValueError as exc:
            raise ValueError(f'{source}: line {line_number}: {exc}') from exc
    if not records:
        raise ValueError('source contains no sentences')
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', nargs='?', type=Path, default=Path('data/pilot_markup.txt'))
    parser.add_argument('output', nargs='?', type=Path, default=Path('data/pilot.jsonl'))
    args = parser.parse_args()
    try:
        records = convert(args.input)
        # Validate everything before opening the output, avoiding partial builds.
        args.output.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records), encoding='utf-8')
    except (OSError, ValueError) as exc:
        parser.exit(1, f'ERROR: {exc}\n')
    print(f'BUILD: {len(records)} records -> {args.output}')


if __name__ == '__main__':
    main()
