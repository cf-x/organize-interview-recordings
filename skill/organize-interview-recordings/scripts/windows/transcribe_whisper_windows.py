#!/usr/bin/env python3
"""Transcribe one media file with faster-whisper and write TXT, JSON, and SRT."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any


def package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "not installed"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, help="Input media file")
    parser.add_argument("output_dir", nargs="?", type=Path, help="Output directory")
    parser.add_argument(
        "--model",
        default=os.getenv("WHISPER_MODEL", "large-v3"),
        help="faster-whisper model name or local directory",
    )
    parser.add_argument(
        "--language",
        default=os.getenv("WHISPER_LANGUAGE", "en"),
        help="Language code or 'auto'",
    )
    parser.add_argument(
        "--initial-prompt",
        default=os.getenv("WHISPER_INITIAL_PROMPT", ""),
    )
    parser.add_argument("--task", choices=("transcribe", "translate"), default="transcribe")
    parser.add_argument("--device", choices=("auto", "cuda", "cpu"), default="auto")
    parser.add_argument("--compute-type", default="auto")
    parser.add_argument("--beam-size", type=int, default=5)
    parser.add_argument("--no-vad", action="store_true")
    parser.add_argument(
        "--version",
        action="version",
        version=f"faster-whisper {package_version('faster-whisper')}",
    )
    args = parser.parse_args()
    if args.input is None:
        parser.error("input is required")
    return args


def format_srt_time(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def word_payload(word: Any) -> dict[str, Any]:
    return {
        "start": getattr(word, "start", None),
        "end": getattr(word, "end", None),
        "word": getattr(word, "word", ""),
        "probability": getattr(word, "probability", None),
    }


def main() -> int:
    args = parse_args()
    input_path = args.input.expanduser().resolve()
    if not input_path.is_file():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 2

    try:
        import ctranslate2
        from faster_whisper import WhisperModel
    except ImportError as exc:
        print(f"Whisper runtime is incomplete: {exc}", file=sys.stderr)
        return 2

    cuda_available = ctranslate2.get_cuda_device_count() > 0
    if args.device == "cuda" and not cuda_available:
        print("CUDA was requested but is not available to CTranslate2.", file=sys.stderr)
        return 2
    device = "cuda" if cuda_available and args.device != "cpu" else "cpu"
    compute_type = args.compute_type
    if compute_type == "auto":
        compute_type = "float16" if device == "cuda" else "int8"

    output_dir = args.output_dir
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path.cwd() / "whisper-output" / f"{input_path.stem}_{timestamp}"
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Model: {args.model}")
    print(f"Device: {device} ({compute_type})")
    print(f"Input: {input_path}")
    print(f"Output: {output_dir}")

    model = WhisperModel(args.model, device=device, compute_type=compute_type)
    language = None if args.language.lower() == "auto" else args.language
    segments_iter, info = model.transcribe(
        str(input_path),
        language=language,
        task=args.task,
        initial_prompt=args.initial_prompt or None,
        beam_size=args.beam_size,
        word_timestamps=True,
        vad_filter=not args.no_vad,
        condition_on_previous_text=True,
    )
    segments = list(segments_iter)

    text = "".join(segment.text for segment in segments).strip()
    stem = f"{input_path.stem}_whisper-large-v3"
    (output_dir / f"{stem}.txt").write_text(text + "\n", encoding="utf-8")

    json_segments = []
    srt_lines: list[str] = []
    for index, segment in enumerate(segments, start=1):
        segment_text = segment.text.strip()
        json_segments.append(
            {
                "id": getattr(segment, "id", index - 1),
                "start": segment.start,
                "end": segment.end,
                "text": segment_text,
                "words": [word_payload(word) for word in (segment.words or [])],
            }
        )
        srt_lines.extend(
            [
                str(index),
                f"{format_srt_time(segment.start)} --> {format_srt_time(segment.end)}",
                segment_text,
                "",
            ]
        )

    payload = {
        "backend": "faster-whisper",
        "model": args.model,
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "text": text,
        "segments": json_segments,
    }
    (output_dir / f"{stem}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / f"{stem}.srt").write_text("\n".join(srt_lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
