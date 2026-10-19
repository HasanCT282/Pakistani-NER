"""Split pilot records by group, keeping translations together."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.validate_data import validate_file


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', nargs='?', type=Path, default=Path('data/pilot.jsonl'))
    parser.add_argument('--assignment', type=Path, default=Path('data/split_assignment.json'))
    parser.add_argument('--output-dir', type=Path, default=Path('data/splits'))
    args = parser.parse_args()
    try:
        _, errors = validate_file(args.input)
        if errors:
            raise ValueError('; '.join(errors))
        records = [json.loads(line) for line in args.input.read_text(encoding='utf-8').splitlines()]
        assignment = json.loads(args.assignment.read_text(encoding='utf-8'))
        if not isinstance(assignment, dict) or set(assignment) != {'dev', 'test'}:
            raise ValueError('assignment must contain exactly dev and test lists')
        for name, values in assignment.items():
            if not isinstance(values, list) or any(not isinstance(g, str) for g in values):
                raise ValueError(f'{name} must be a list of group strings')
            if len(values) != len(set(values)):
                raise ValueError(f'duplicate {name} group')
        dev, test = set(assignment['dev']), set(assignment['test'])
        if dev & test:
            raise ValueError('dev and test groups overlap')
        if any(not isinstance(r.get('group'), str) or not r['group'] for r in records):
            raise ValueError('every record needs a nonempty group string')
        unknown = (dev | test) - {r['group'] for r in records}
        if unknown:
            raise ValueError(f'unknown assigned groups: {sorted(unknown)}')
        buckets = {name: [] for name in ('train', 'dev', 'test')}
        for record in records:
            group = record['group']
            name = 'dev' if group in dev else 'test' if group in test else 'train'
            buckets[name].append(record)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, rows in buckets.items():
            path = args.output_dir / f'pilot_{name}.jsonl'
            path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')
            print(f'SPLIT: {name}: {len(rows)} records, {len({r["group"] for r in rows})} groups -> {path}')
    except (OSError, ValueError) as exc:
        parser.exit(1, f'ERROR: {exc}\n')


if __name__ == '__main__':
    main()
