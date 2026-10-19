"""Count records, languages and entity mentions in one or more JSONL files."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.labels import ENTITY_TYPES
from scripts.validate_data import validate_file


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', type=Path)
    args = parser.parse_args()
    try:
        for path in args.files:
            count, errors = validate_file(path)
            if errors:
                raise ValueError(f'{path}: ' + '; '.join(errors))
            languages, mentions = Counter(), Counter()
            for line in path.read_text(encoding='utf-8').splitlines():
                record = json.loads(line)
                languages[record.get('lang', '(missing)')] += 1
                # Each B tag begins one mention, regardless of its token length.
                mentions.update(tag[2:] for tag in record['ner_tags'] if tag.startswith('B-'))
            print(f'{path}: records={count}; languages=' + json.dumps(dict(sorted(languages.items()))))
            for kind in ENTITY_TYPES:
                print(f'  {kind}: {mentions[kind]}' + (' ZERO' if mentions[kind] == 0 else ''))
    except (OSError, ValueError) as exc:
        parser.exit(1, f'ERROR: {exc}\n')


if __name__ == '__main__':
    main()
