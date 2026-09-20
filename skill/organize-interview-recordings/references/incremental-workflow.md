# Incremental execution

Paths below are examples, resolved in the user's workspace. Scripts live under the installed skill. Generated state and backups are private workspace artifacts, never part of the skill release.

## Private settings

Optional `local-settings.json` beside `SKILL.md` uses `authorized_read_only_roots` (an array of previously authorized directory paths), `QWEN_ASR_COMMAND` and `WHISPER_ASR_COMMAND` (executable paths). Load only when resolving sources/runtime; do not print its contents in reports or copy it to a release. Preserve existing user authorization; a path in this file alone cannot authorize reading a new root.

## Fingerprints and selected backups

Use `scripts/workspace_state.py` instead of regenerating backup/fingerprint code. It hashes explicit existing files; it never scans a private root automatically. Exclude symlinks when selecting files. Large media are streamed through SHA-256 locally, never printed.

```bash
python scripts/workspace_state.py check --root /workspace --file transcripts/session.json --file notes/session.md --manifest /workspace/.interview-state/session-note.json --version note-v2
python scripts/workspace_state.py backup --root /workspace --file notes/session.md --file topics/project.md --manifest /workspace/backups/unique-run/manifest.json
python scripts/workspace_state.py verify-backup --root /workspace --manifest /workspace/backups/unique-run/manifest.json
```

Use `save` with the same files/version only after successful validation. Include both inputs and expected output files plus relevant local fact sources. Include model/options identity in the ASR stage version; use separate ASR, note and collection states. A missing output means recompute, even if input hashes match. The helper reports byte changes only; the agent decides their relevance. It does not verify semantic correctness.

On first use, inspect existing artifacts before recording their baseline. Do not rerun valid ASR merely because a manifest does not yet exist. Select only already-existing files for backup. New files are tracked as creations in the completion report, not fabricated as backups. Do not use all-current-note name equality to validate a partial backup.

## Source merging

```bash
python scripts/merge_transcripts.py --source system=/workspace/transcripts/system.json --source microphone=/workspace/transcripts/microphone.json --role system=面试官 --role microphone=候选人 --duration 600 --output /workspace/transcripts/session-merged
```

Inputs use `segments: [{start, end, text, ...}]` in seconds. Omit roles until confirmed. This writes a new `.json`, `.txt`, `.srt` without overwriting any existing output. It retains overlaps and zero-duration units, reports the latter, and rejects nonfinite/reversed/out-of-bounds timestamps. Review zero-duration subtitles; use source decoding blocks when word alignment is unreliable. It does not invent durations or remove echo.

## Context budget

- Return counts, changed paths and short QC summaries; do not print complete JSON, backup manifests or duplicate TXT/SRT/JSON bodies.
- Read one canonical transcript; use its time ranges to fetch uncertain evidence only. For very long interviews, process coherent question windows and keep a compact coverage ledger so follow-ups are not lost at window boundaries.
- Search authorized sources with question-specific terms, then read relevant sections. Reuse confirmed facts with source locations and evidence levels.
- Keep deterministic transformation in reusable scripts. Session-specific output data belongs in workspace artifacts, not newly generated copies of scripts.
- Full semantic review is appropriate for first-time indexing, uncertain matches or requested global cleanup. Normal updates inspect candidate blocks and modified dependencies.
