---
name: organize-interview-recordings
description: 本地转写面试录屏或录音，复用同场笔记，区分现场回答与 AI 优化，生成复盘并将问题增量去重到本地题库。用于面试录屏整理、问答恢复和跨场题库维护；仅在明确要求时同步飞书。
---

# Organize Interview Recordings

## Invariants

- Keep media local; preserve source recordings, raw transcripts and original notes. Back up only existing files that will change, before writing. New files have no pre-edit backup.
- Reuse the canonical session note and stable filenames. Preserve historical mistakes in the recorded-answer field; correct them only in a visibly purple AI section.
- Existing notes are reuse candidates, not stronger evidence than audio or video. Resolve disputed history from primary evidence; if unavailable, retain the conflict or `未保留完整回答`. Local AI-written material never becomes a verified fact merely by being saved.
- AI answers use keyword-led bullets and plain Chinese. Preserve conditions, evidence and responsibility boundaries. No invented historical answers, default experiment gains, metaphors or decorative prose.
- One primary collection owner per semantic question. Full history belongs in session notes; topic collections retain consolidated learning points and source links.
- Search the workspace and user-authorized read-only roots only. An optional untracked `local-settings.json` beside this file can retain previously authorized roots and runtime command paths; it cannot grant new permission. Never publish it, recordings, notes, resumes, company material, private paths, credentials or authorization artifacts.
- Online sync is a separate, explicitly requested action. No automatic connector setup or online writes during local work.

## Choose the smallest workflow

Read each relevant reference once; execute helpers without loading their source unless debugging.

| Task | Read |
| --- | --- |
| New audio or transcription repair | [asr-runtime.md](references/asr-runtime.md); platform setup only if runtime is missing/broken |
| Create or edit Q&A | [output-standard.md](references/output-standard.md) |
| Retrieve project facts or update topic collections | [local-collection.md](references/local-collection.md) |
| Incremental state, backups or helper commands | [incremental-workflow.md](references/incremental-workflow.md) |
| Requested Feishu operation | [lark-sync.md](references/lark-sync.md) completely, then its required installed skills |

An existing transcript does not require another ASR run. A wording edit does not require rebuilding all sessions or collections. A sync-only task does not require rewriting unchanged local notes.

## Local execution

1. Inspect workspace instructions and identify the requested sessions, canonical notes and changed dependencies. Exclude backups, caches and drafts from normal discovery. Use filename/heading inventories first; read relevant sections, not every transcript format or the entire fact library.
2. Reuse valid artifacts. Compare explicit input fingerprints and relevant rule versions with the last successful state. Missing/corrupt outputs, new source evidence or a relevant rule change invalidate the affected stage only. Do not mark a stage complete before validation. Do not globally rewrite legacy notes for a style change unless requested.
3. Back up the selected existing write targets with the helper. Transcribe only missing/invalid source tracks. Preserve overlaps, source labels and raw output; inspect uncertainty windows rather than repeating a full transcription.
4. Read one compact timestamped transcript for reconstruction. Consult raw segments/audio/frames for disputed roles, names, metrics, code and missing turns. Keep all substantive questions and follow-ups; token savings must not silently drop evidence.
5. Write Q&A using the output standard. Give each question a stable explicit anchor and evidence time range when available. End with `考察重点`, `主要问题`, `改进方向`, grounded in this session.
6. Update only relevant primary collection blocks and index entries. If only a source link is new, keep the existing optimized answer. Report inserted/merged/linked/deferred counts separately from source-question counts.
7. Audit changed notes with `python scripts/audit_interview_notes.py <notes-dir> --name-regex <selection> --require-purple-ai --require-bullets`. Verify the backup manifest and changed collection links/owners separately. The audit checks structure, not factual correctness or semantic equivalence. Resolve failures or explain evidence-dependent exceptions; save successful state last.

Report changed outputs, validation, backup location and unresolved evidence briefly. For requested online sync, include document links, pre/post revisions and read-back results. Do not expose local private details in public release notes.
