#!/usr/bin/env python3
"""Transcribe one media file with Qwen3-ASR and write TXT, JSON, and SRT."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any


@dataclass
class Segment:
    start: float
    end: float
    text: str


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
        default=os.getenv("QWEN_ASR_MODEL", "Qwen/Qwen3-ASR-1.7B"),
        help="Hugging Face model ID or local directory",
    )
    parser.add_argument(
        "--aligner-model",
        default=os.getenv("QWEN_ALIGNER_MODEL", "Qwen/Qwen3-ForcedAligner-0.6B"),
        help="Forced-aligner model ID or local directory",
    )
    parser.add_argument(
        "--language",
        default=os.getenv("QWEN_ASR_LANGUAGE", "Chinese"),
        help="Language name or 'auto'",
    )
    parser.add_argument("--device", choices=("auto", "cuda", "cpu"), default="auto")
    parser.add_argument("--no-timestamps", action="store_true")
    parser.add_argument("--max-new-tokens", type=int, default=4096)
    parser.add_argument(
        "--version",
        action="version",
        version=f"qwen-asr {package_version('qwen-asr')}",
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


def join_tokens(parts: list[str]) -> str:
    text = "".join(parts).strip()
    return " ".join(text.split())


def aligned_items_to_segments(items: Any) -> list[Segment]:
    segments: list[Segment] = []
    current_text: list[str] = []
    current_start: float | None = None
    current_end = 0.0

    for item in items or []:
        token = str(getattr(item, "text", "") or "")
        start = float(getattr(item, "start_time", current_end) or current_end)
        end = float(getattr(item, "end_time", start) or start)
        if current_start is None:
            current_start = start

        gap = max(0.0, start - current_end) if current_text else 0.0
        candidate = join_tokens(current_text + [token])
        should_flush = bool(current_text) and (
            gap > 1.2
            or end - current_start >= 8.0
            or len(candidate) >= 72
        )
        if should_flush:
            segments.append(Segment(current_start, current_end, join_tokens(current_text)))
            current_text = []
            current_start = start

        current_text.append(token)
        current_end = end
        if token.rstrip().endswith(("。", "！", "？", ".", "!", "?")):
            segments.append(Segment(current_start, current_end, join_tokens(current_text)))
            current_text = []
            current_start = None

    if current_text and current_start is not None:
        segments.append(Segment(current_start, current_end, join_tokens(current_text)))
    return [segment for segment in segments if segment.text]


def write_outputs(
    output_dir: Path,
    stem: str,
    text: str,
    language: str,
    model_name: str,
    segments: list[Segment],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{stem}.txt").write_text(text.strip() + "\n", encoding="utf-8")

    payload = {
        "backend": "qwen-asr",
        "model": model_name,
        "language": language,
        "text": text,
        "segments": [asdict(segment) for segment in segments],
    }
    (output_dir / f"{stem}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if segments:
        srt_lines: list[str] = []
        for index, segment in enumerate(segments, start=1):
            srt_lines.extend(
                [
                    str(index),
                    f"{format_srt_time(segment.start)} --> {format_srt_time(segment.end)}",
                    segment.text,
                    "",
                ]
            )
        (output_dir / f"{stem}.srt").write_text("\n".join(srt_lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    input_path = args.input.expanduser().resolve()
    if not input_path.is_file():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 2

    try:
        import torch
        from qwen_asr import Qwen3ASRModel
    except ImportError as exc:
        print(f"Qwen runtime is incomplete: {exc}", file=sys.stderr)
        return 2

    use_cuda = torch.cuda.is_available() and args.device != "cpu"
    if args.device == "cuda" and not torch.cuda.is_available():
        print("CUDA was requested but is not available.", file=sys.stderr)
        return 2

    device_map = "cuda:0" if use_cuda else "cpu"
    if use_cuda:
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    else:
        dtype = torch.float32
    output_dir = args.output_dir
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path.cwd() / "asr-output" / f"{input_path.stem}_qwen3_{timestamp}"
    output_dir = output_dir.expanduser().resolve()

    model_kwargs: dict[str, Any] = {
        "dtype": dtype,
        "device_map": device_map,
        "max_inference_batch_size": 1,
        "max_new_tokens": args.max_new_tokens,
    }
    if not args.no_timestamps:
        model_kwargs["forced_aligner"] = args.aligner_model
        model_kwargs["forced_aligner_kwargs"] = {
            "dtype": dtype,
            "device_map": device_map,
        }

    print(f"Model: {args.model}")
    print(f"Device: {device_map}")
    print(f"Input: {input_path}")
    print(f"Output: {output_dir}")

    model = Qwen3ASRModel.from_pretrained(args.model, **model_kwargs)
    language = None if args.language.lower() == "auto" else args.language
    results = model.transcribe(
        audio=str(input_path),
        language=language,
        return_time_stamps=not args.no_timestamps,
    )
    if not results:
        print("The model returned no transcription.", file=sys.stderr)
        return 1

    result = results[0]
    segments = aligned_items_to_segments(getattr(result, "time_stamps", None))
    stem = f"{input_path.stem}_qwen3-asr"
    write_outputs(
        output_dir,
        stem,
        str(getattr(result, "text", "") or ""),
        str(getattr(result, "language", "") or ""),
        args.model,
        segments,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
