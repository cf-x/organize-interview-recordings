#!/usr/bin/env python3
"""Build a compact heading catalog or retrieve lexical candidates; no semantic merge."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def terms(text):
    text = text.casefold()
    return set(re.findall(r'[a-z0-9_]+', text)) | {text[i:i+2] for i in range(len(text)-1) if all('\u4e00' <= c <= '\u9fff' for c in text[i:i+2])}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['build', 'query'])
    p.add_argument('--root', type=Path, default=Path('.'))
    p.add_argument('--file', action='append', default=[])
    p.add_argument('--catalog', type=Path, required=True)
    p.add_argument('--text', default='')
    p.add_argument('--limit', type=int, default=8)
    args = p.parse_args()
    try:
        if args.command == 'build':
            if not args.file:
                raise ValueError('Explicit primary collection files required')
            rows = []
            root = args.root.resolve()
            for name in dict.fromkeys(args.file):
                path = (root / name).resolve()
                relative = str(path.relative_to(root))
                content = path.read_bytes()
                digest = hashlib.sha256(content).hexdigest()
                text = content.decode('utf-8-sig')
                # Ignore fenced examples. Only H2 primary questions are indexed.
                visible = re.sub(r'(?ms)^```.*?^```[^\n]*$', '', text)
                headings = list(re.finditer(r'(?m)^## (.+)$', visible))
                for i, match in enumerate(headings):
                    block = visible[match.end():headings[i+1].start() if i+1 < len(headings) else len(visible)]
                    anchors = re.findall(r'<a\s+id=[\"\']([^\"\']+)[\"\']\s*>', block)
                    rows.append({'owner': relative, 'title': match[1], 'anchors': anchors,
                                 'source_sha256': digest})
            args.catalog.parent.mkdir(parents=True, exist_ok=True)
            temporary = args.catalog.with_suffix(args.catalog.suffix + '.tmp')
            with temporary.open('x', encoding='utf-8') as stream:
                json.dump(rows, stream, ensure_ascii=False, indent=2)
            temporary.replace(args.catalog)
            print(f'questions={len(rows)}')
        else:
            if not args.text or args.limit < 1:
                raise ValueError('Query text and positive limit required')
            query = terms(args.text)
            rows = json.loads(args.catalog.read_text())
            ranked = [(len(query & terms(row['title'])), row) for row in rows]
            ranked.sort(key=lambda item: item[0], reverse=True)
            print(json.dumps({'lexical_only': True, 'candidates': [dict(row, score=score) for score, row in ranked[:args.limit] if score]}, ensure_ascii=False))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        p.exit(1, f'ERROR: {exc}\n')


if __name__ == '__main__':
    main()
