#!/usr/bin/env python3
"""Audit structured interview notes without modifying them."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


REQUIRED_HEADINGS = ("## 基本信息", "## 问答记录", "## 面试总结")
NOISE_PATTERNS = (
    "感谢观看",
    "请不吝点赞",
    "订阅 订阅",
    "打赏 打赏",
)
LOCAL_LINK_RE = re.compile(r"\]\(<([^>]+)>\)|\]\(([^)]+)\)")
QUESTION_BLOCK_RE = re.compile(r"(?ms)^### .+?(?=^### |^## 面试总结|\Z)")
AI_LABEL_RE = re.compile(r"🟣\s*AI\s*(?:生成|补充|推测|推定|重建)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notes_dir", type=Path)
    parser.add_argument("--backup-dir", type=Path)
    parser.add_argument(
        "--name-regex",
        default=r"^\d{4}-?\d{2}-?\d{2}.*\.md$",
        help="Regex selecting canonical interview note filenames.",
    )
    parser.add_argument(
        "--require-purple-ai",
        action="store_true",
        help="Require each AI field to use the purple provenance marker.",
    )
    parser.add_argument('--require-bullets', action='store_true', help='Strict current style for selected new/changed notes only')
    parser.add_argument('--links-file', action='append', type=Path, default=[], help='Also check links and explicit anchors in a changed collection/index')
    return parser.parse_args()


def anchors(text):
    result = set(re.findall(r'<a\s+id=["\']([^"\']+)["\']', text))
    counts = {}
    for heading in re.findall(r'(?m)^#{1,6} (.+)$', text):
        slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        result.add(slug + (f'-{count}' if count else ''))
    return result


def link_errors(note, text):
    errors = []
    count = 0
    ids = re.findall(r'<a\s+id=["\']([^"\']+)["\']', text)
    if len(ids) != len(set(ids)):
        errors.append(f'{note.name}: duplicate explicit anchors')
    for match in LOCAL_LINK_RE.finditer(text):
        target = (match.group(1) or match.group(2)).strip()
        is_windows_path = bool(re.match(r'^[A-Za-z]:[\\/]', target))
        if (urlsplit(target).scheme and not is_windows_path) or target.startswith('//'):
            continue
        path, _, fragment = target.partition('#')
        resolved = (note.parent / unquote(path)).resolve() if path else note.resolve()
        count += 1
        if not resolved.is_file():
            errors.append(f'{note.name}: broken link: {target}')
        elif fragment and resolved.suffix.lower() == '.md':
            if unquote(fragment) not in anchors(resolved.read_text(encoding='utf-8-sig')):
                errors.append(f'{note.name}: missing link anchor: {target}')
    return errors, count


def main() -> int:
    args = parse_args()
    if not args.notes_dir.is_dir():
        print(f"ERROR: notes directory does not exist: {args.notes_dir}")
        return 2

    try:
        selector = re.compile(args.name_regex)
    except re.error as exc:
        print(f"ERROR: invalid --name-regex: {exc}")
        return 2

    notes = sorted(
        path for path in args.notes_dir.glob("*.md") if selector.match(path.name)
    )
    errors: list[str] = []
    question_count = 0
    link_count = 0

    if not notes:
        errors.append("no canonical interview notes matched --name-regex")

    for note in notes:
        text = note.read_text(encoding="utf-8-sig")
        for heading in REQUIRED_HEADINGS:
            if not re.search(rf"(?m)^{re.escape(heading)}\s*$", text):
                errors.append(f"{note.name}: missing {heading}")
        if "AI 补充说明" not in text:
            errors.append(f"{note.name}: missing AI supplement disclosure")

        blocks = QUESTION_BLOCK_RE.findall(text)
        question_count += len(blocks)
        if not blocks:
            errors.append(f'{note.name}: no question blocks')
        for field in ('考察重点', '主要问题', '改进方向'):
            if not re.search(r'\*\*' + field + r'[：:]?\*\*[ \t]*\S', text):
                errors.append(f'{note.name}: missing or empty summary field: {field}')
        for block in blocks:
            title = block.splitlines()[0]
            if not re.search(r"\*\*我的(?:回答|作答|问题)", block):
                errors.append(f"{note.name}: missing recorded-answer field in {title}")
            if not re.search(r"AI\s*(?:补充|生成|推测|推定|重建)", block):
                errors.append(f"{note.name}: missing AI optimization in {title}")
            if not re.search(r'\*\*(?:面试官问|题目|我的问题)', block):
                errors.append(f'{note.name}: missing question field in {title}')
            if '**我的问题' in block and '**面试官回答' not in block:
                errors.append(f'{note.name}: missing interviewer answer in {title}')
            if not re.search(r'AI\s*(?:生成|补充)[^\n<]*(?:回答|解法|追问|问法|优化)', block):
                errors.append(f'{note.name}: missing AI answer (reconstruction alone is insufficient) in {title}')
            if args.require_bullets:
                for line in block.splitlines():
                    if re.search(r'AI\s*(?:生成|补充)[^<]*(?:回答|解法|追问|问法|优化)', line):
                        after = block[block.index(line) + len(line):].lstrip()
                        if not line.rstrip().endswith('</span>') or line.lstrip().startswith('- ') or not re.match(r'- \*\*[^*]+\*\*[ \t]*\S', after):
                            errors.append(f'{note.name}: AI answer must use standalone label and keyword bullets in {title}')
            if args.require_purple_ai:
                ai_lines = [line for line in block.splitlines() if AI_LABEL_RE.search(line)]
                has_purple_label = bool(ai_lines) and all(
                    re.search(r'<span[^>]*color\s*:\s*#7c3aed[^>]*>.*?🟣\s*AI.*?</span>', line, re.I)
                    for line in ai_lines
                )
                if not has_purple_label:
                    errors.append(f"{note.name}: missing purple AI label in {title}")

        for noise in NOISE_PATTERNS:
            if noise in text:
                errors.append(f"{note.name}: transcript noise found: {noise}")

        found, count = link_errors(note, text)
        errors.extend(found)
        link_count += count

    for extra in args.links_file:
        if not extra.is_file():
            errors.append(f'missing link-check file: {extra}')
            continue
        found, count = link_errors(extra, extra.read_text(encoding='utf-8-sig'))
        errors.extend(found)
        link_count += count

    if args.backup_dir:
        if not args.backup_dir.is_dir():
            errors.append(f"backup directory missing: {args.backup_dir}")
        else:
            current_names = {path.name for path in notes}
            backup_names = {
                path.name
                for path in args.backup_dir.glob("*.md")
                if selector.match(path.name)
            }
            missing = sorted(current_names - backup_names)
            extra = sorted(backup_names - current_names)
            if missing:
                errors.append("backup missing: " + ", ".join(missing))
            if extra:
                errors.append("backup has unmatched notes: " + ", ".join(extra))

    print(f"notes={len(notes)} questions={question_count} local_links={link_count}")
    if errors:
        print(f"errors={len(errors)}")
        for error in errors:
            print(f"- {error}")
        return 1
    print("errors=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
