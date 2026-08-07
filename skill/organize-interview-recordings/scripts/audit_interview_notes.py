#!/usr/bin/env python3
"""Audit structured interview notes without modifying them."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


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
    return parser.parse_args()


def check_link(note: Path, target: str) -> Path | None:
    target = target.split("#", 1)[0].strip()
    if not target or re.match(r"^(?:https?://|mailto:|#)", target):
        return None
    return (note.parent / target).resolve()


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
        for block in blocks:
            title = block.splitlines()[0]
            if not re.search(r"\*\*我的(?:回答|作答|问题)", block):
                errors.append(f"{note.name}: missing recorded-answer field in {title}")
            if not re.search(r"AI\s*(?:补充|生成|推测|推定|重建)", block):
                errors.append(f"{note.name}: missing AI optimization in {title}")
            if args.require_purple_ai:
                has_purple_label = "#7C3AED" in block and AI_LABEL_RE.search(block)
                if not has_purple_label:
                    errors.append(f"{note.name}: missing purple AI label in {title}")

        for noise in NOISE_PATTERNS:
            if noise in text:
                errors.append(f"{note.name}: transcript noise found: {noise}")

        for match in LOCAL_LINK_RE.finditer(text):
            target = match.group(1) or match.group(2)
            resolved = check_link(note, target)
            if resolved is None:
                continue
            link_count += 1
            if not resolved.exists():
                errors.append(f"{note.name}: broken link: {target}")

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
