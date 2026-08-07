from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skill" / "organize-interview-recordings"
AUDIT_SCRIPT = SKILL_ROOT / "scripts" / "audit_interview_notes.py"
QWEN_SCRIPT = SKILL_ROOT / "scripts" / "windows" / "transcribe_qwen_windows.py"
WHISPER_SCRIPT = SKILL_ROOT / "scripts" / "windows" / "transcribe_whisper_windows.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


VALID_NOTE = """# 2026-08-07 Example Round

## 基本信息

- <span style="color:#7C3AED"><strong>🟣 AI 补充说明：</strong></span> AI 内容已标记。

## 问答记录

### 1. 项目取舍

- **面试官问：** 为什么选择这个方案？
- **我的回答（整理）：** 因为时间有限。
- <span style="color:#7C3AED"><strong>🟣 AI 生成优化回答：</strong></span> 补充约束和证据。

## 面试总结

- **考察重点：** 方案判断
- **主要问题：** 证据不足
- **改进方向：** 补做对比实验
"""


class AuditScriptTests(unittest.TestCase):
    def run_audit(self, note_text: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            notes = root / "notes"
            backup = root / "backup"
            notes.mkdir()
            backup.mkdir()
            filename = "2026-08-07-example.md"
            (notes / filename).write_text(note_text, encoding="utf-8")
            (backup / filename).write_text(note_text, encoding="utf-8")
            return subprocess.run(
                [
                    sys.executable,
                    str(AUDIT_SCRIPT),
                    str(notes),
                    "--backup-dir",
                    str(backup),
                    "--require-purple-ai",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

    def test_valid_note_passes(self) -> None:
        result = self.run_audit(VALID_NOTE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("errors=0", result.stdout)

    def test_missing_purple_label_fails(self) -> None:
        result = self.run_audit(VALID_NOTE.replace("#7C3AED", "#000000", 2))
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing purple AI label", result.stdout)


class WrapperHelperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.qwen = load_module("qwen_windows_wrapper", QWEN_SCRIPT)
        cls.whisper = load_module("whisper_windows_wrapper", WHISPER_SCRIPT)

    def test_srt_time_format(self) -> None:
        self.assertEqual(self.qwen.format_srt_time(3661.234), "01:01:01,234")
        self.assertEqual(self.whisper.format_srt_time(0), "00:00:00,000")

    def test_qwen_token_grouping(self) -> None:
        class Item:
            def __init__(self, text: str, start: float, end: float) -> None:
                self.text = text
                self.start_time = start
                self.end_time = end

        items = [Item("你好", 0.0, 0.4), Item("。", 0.4, 0.6)]
        segments = self.qwen.aligned_items_to_segments(items)
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0].text, "你好。")


if __name__ == "__main__":
    unittest.main()
