#!/usr/bin/env python3
"""Explicit-file fingerprints and verified incremental backups (stdlib only)."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path


def fingerprint(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def inventory(root, files):
    result = {}
    for name in files:
        original = root / name
        if original.is_symlink():
            raise ValueError('Select real files, not symlinks')
        path = original.resolve()
        relative = str(path.relative_to(root))
        if relative in result:
            raise ValueError('Duplicate file selection')
        if path.is_symlink() or not path.is_file():
            raise ValueError(f'Expected existing file: {relative}')
        result[relative] = fingerprint(path)
    if not result:
        raise ValueError('Select at least one file')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['check', 'save', 'backup', 'verify-backup'])
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--file', action='append', default=[])
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--version', default='1', help='Relevant stage/rule version for check/save')
    args = p.parse_args()
    try:
        root = args.root.resolve()
        if args.command == 'verify-backup':
            saved = json.loads(args.manifest.read_text())
            actual = inventory(args.manifest.parent.resolve(), list(saved['files']))
            if actual != saved['files']:
                raise ValueError('Backup hash mismatch')
            print(f"verified={len(actual)}")
            return
        files = inventory(root, args.file)
        state = {'version': args.version, 'files': files}
        if args.command == 'check':
            old = json.loads(args.manifest.read_text()) if args.manifest.exists() else {}
            changed = sorted(k for k in set(files) | set(old.get('files', {})) if files.get(k) != old.get('files', {}).get(k))
            print(json.dumps({'unchanged': old == state, 'changed': changed,
                              'version_changed': old.get('version') != args.version}))
        elif args.command == 'save':
            args.manifest.parent.mkdir(parents=True, exist_ok=True)
            temp = args.manifest.with_suffix(args.manifest.suffix + '.tmp')
            with temp.open('x', encoding='utf-8') as stream:
                stream.write(json.dumps(state, ensure_ascii=False, indent=2))
            temp.replace(args.manifest)
            print(f'saved={len(files)}')
        else:
            destination = args.manifest.parent.resolve()
            if destination.exists():
                raise ValueError('Backup destination must be a new directory')
            if args.manifest.name in files:
                raise ValueError('Backup manifest collides with a source filename')
            destination.mkdir(parents=True)
            for name, expected in files.items():
                target = destination / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / name, target)
                if fingerprint(target) != expected:
                    raise ValueError(f'Backup changed during copy: {name}')
            args.manifest.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f'backed_up={len(files)}')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        p.exit(1, f'ERROR: {exc}\n')


if __name__ == '__main__':
    main()
