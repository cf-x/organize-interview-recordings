#!/usr/bin/env python3
"""Merge explicit source JSON files. No ASR, cleaning or identity inference."""
import argparse
import json
import math
from pathlib import Path


def stamp(seconds, separator):
    ms = round(seconds * 1000)
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}{separator}{ms % 1000:03d}'


def merge(sources, roles, duration=None):
    result = []
    zero = 0
    if duration is not None and (not math.isfinite(duration) or duration <= 0):
        raise ValueError('duration must be finite and positive')
    for source, path in sources.items():
        data = json.loads(Path(path).read_text(encoding='utf-8-sig'))
        segments = data.get('segments')
        if not isinstance(segments, list) or not segments:
            raise ValueError(f'{source}: no segments')
        for index, segment in enumerate(segments):
            start, end = float(segment['start']), float(segment['end'])
            if not all(map(math.isfinite, (start, end))) or start < 0 or end < start:
                raise ValueError(f'{source}: invalid timestamp at segment {index}')
            if duration is not None and end > duration + 1:
                raise ValueError(f'{source}: segment exceeds media duration')
            if not isinstance(segment.get('text'), str):
                raise ValueError(f'{source}: missing text at segment {index}')
            zero += start == end
            result.append(dict(segment, start=start, end=end, source=source,
                               role=roles.get(source, source), source_segment_index=index))
    result.sort(key=lambda s: (s['start'], s['source'], s['source_segment_index']))
    return {'segments': result, 'qc': {'zero_duration_units': zero, 'segments': len(result)},
            'role_basis': 'Explicit caller mapping; otherwise source label only.'}


def pairs(values):
    result = {}
    for value in values:
        key, sep, item = value.partition('=')
        if not sep or not key or not item or key in result:
            raise ValueError('Expected unique SOURCE=VALUE pairs')
        result[key] = item
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', action='append', required=True, help='SOURCE=JSON_PATH')
    p.add_argument('--role', action='append', default=[], help='SOURCE=CONFIRMED_ROLE')
    p.add_argument('--duration', type=float)
    p.add_argument('--output', type=Path, required=True, help='New output basename, without extension')
    args = p.parse_args()
    try:
        sources, roles = pairs(args.source), pairs(args.role)
        if set(roles) - set(sources):
            raise ValueError('Role supplied for an unknown source')
        data = merge(sources, roles, args.duration)
        targets = [Path(str(args.output) + ext) for ext in ('.json', '.txt', '.srt')]
        if any(path.exists() for path in targets):
            raise ValueError('Output exists; choose a new basename to preserve originals')
        rows = data['segments']
        payloads = [json.dumps(data, ensure_ascii=False, indent=2) + '\n',
                    '\n'.join(f"[{stamp(s['start'], '.')}–{stamp(s['end'], '.')}] {s['role']} ({s['source']}): {s['text']}" for s in rows) + '\n',
                    '\n'.join(f"{i}\n{stamp(s['start'], ',')} --> {stamp(s['end'], ',')}\n[{s['role']}/{s['source']}] {s['text']}\n" for i, s in enumerate(rows, 1))]
        args.output.parent.mkdir(parents=True, exist_ok=True)
        for path, payload in zip(targets, payloads):
            with path.open('x', encoding='utf-8') as stream:
                stream.write(payload)
        print(json.dumps(data['qc']))
    except (ValueError, KeyError, OSError, TypeError) as exc:
        p.exit(1, f'ERROR: {exc}\n')


if __name__ == '__main__':
    main()
