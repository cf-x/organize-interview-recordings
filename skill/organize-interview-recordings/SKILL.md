---
name: organize-interview-recordings
description: 本地批量整理面试录屏、录音和面试笔记：按语音主导语言调用本机 ASR（中文优先 Qwen3-ASR，英文优先 Whisper large-v3）转写 MP4/MKV/MOV/M4A/WAV，复用同场笔记，去除转写噪声，只保留有复习价值的面试问题，将录音证据与 AI 优化/重建分开，为缺失实验细节提供明确标注的合理范围，并生成每场复盘、总索引和完整性审计；仅在用户明确要求且本机已经配置兼容工具时增量同步到飞书。用户提到面试录屏转写、本地 ASR/Whisper 面试复盘、整理面试问题、一问一答面经、批量总结面试、从录音恢复问答或同步/优化飞书面试笔记时使用。
---

# Organize Interview Recordings

## Core rules

1. Keep every source recording, transcript, and original note. Back up notes before rewriting; never delete originals.
2. Keep media local by default. Select the command by the host operating system and dominant spoken language; read `references/asr-runtime.md` before transcription.
3. Reuse an existing note for the same interview instead of creating a competing document.
4. Separate evidence from reconstruction:
   - `我的回答（整理）` must remain faithful to the recording or original note.
   - `AI 补充的更好回答/优化点` may repair wording, add missing reasoning, and estimate plausible ranges.
5. Never present an AI estimate as a company log, historical quote, or exact result.
6. Keep only questions useful for future interviews. Remove greetings, logistics chatter, repeated prompts, filler, transcription artifacts, and closing pleasantries unless they reveal a meaningful HR constraint.
7. Treat online documents as a separate write surface. Update them only when the user requests online sync; prefer incremental edits and never overwrite or delete an online source by default.
8. Mark every AI-generated answer, estimate, and reconstruction with the purple conventions in `references/output-standard.md`, locally and online.
9. Never place recordings, transcripts, resumes, credentials, authorization URLs, QR codes, or model caches in a public repository.

Read `references/output-standard.md` before writing or rewriting interview notes. Read `references/asr-runtime.md` before any transcription or runtime repair. Read `references/lark-sync.md` completely before any Feishu/Lark authentication, lookup, creation, or update.

## Workflow

### 1. Inventory before writing

- Enumerate recordings, existing TXT/SRT/JSON transcripts, interview notes, resumes, project summaries, papers, internship notes, and interview-preparation documents.
- Map each recording to one canonical note by date, organization, and round. Record note-only sessions separately.
- Prefer `rg --files` and structured JSON/SRT parsing over ad hoc text extraction.
- Inspect workspace instructions before modifying files.

### 2. Back up the notes

- Copy every note in scope to a timestamped backup directory before rewriting.
- Verify source and backup counts and filenames match.
- Never put generated notes inside the backup directory.

### 3. Transcribe locally

- Choose the model from the spoken language, not the requested note language.
- For Chinese-dominant speech, including Mandarin with English technical terms, use the configured Qwen3-ASR command and `Qwen/Qwen3-ASR-1.7B` by default.
- For English-dominant speech, use the configured Whisper large-v3 command and force `en` unless automatic detection is intentional.
- Resolve commands using `QWEN_ASR_COMMAND` and `WHISPER_ASR_COMMAND` when set. Otherwise follow the platform command table in `references/asr-runtime.md`.
- If the dominant language is unclear, inspect existing notes, metadata, or one short representative sample. Treat mixed speech as Chinese when Mandarin carries most substantive content; otherwise treat it as English. Do not silently run two full passes.
- Produce TXT, SRT, and structured JSON with timestamps when the selected runtime supports them. Resume from valid outputs instead of retranscribing everything.
- Enable diarization only when speaker labels materially help and the runtime is configured for it. Treat overlaps and short-turn boundaries as fallible.
- Inspect audio duration, silence, transcript density, repeated phrases, and timestamps. Treat repeated phrases such as `感谢观看`, `请不吝点赞`, or hundreds of identical tokens as hallucination.
- If audio is silent or unusable, recover visible questions from video frames only when possible and clearly label the source.

### 4. Reconstruct each interview

Use this source priority:

1. Existing same-session interview note
2. Valid transcript and speaker sequence
3. Visible recording frames or coding prompt
4. Local project, internship, paper, and preparation materials
5. General technical knowledge

Infer speaker roles from question/answer flow, but do not invent a historical answer. If the answer is absent, write `未保留完整回答`.

### 5. Write structured Q&A

- Follow the template and labels in `references/output-standard.md`.
- Consolidate repeated follow-ups when they test the same capability.
- Preserve weaknesses in `我的回答（整理）`; put corrections only in the AI section.
- For candidate questions, use `我的问题`, `面试官回答`, and `AI 补充的更好问法/追问`.
- Make optimized answers directly speakable: problem, decision, evidence, tradeoff, boundary, and next step.

### 6. Handle facts and missing experiment details

- Use exact values only when local source material provides them, and keep wording consistent across sessions.
- When the user confirms an experiment was completed but local logs are unavailable, provide a technically plausible range and label it `AI 推定的合理范围`.
- Prefer relative ranges and conditions over fake precision, for example `相对 WER 改善约 3%-8%` instead of `提升 6.37%`.
- Preserve contradictory historical claims in `我的回答（整理）`, then give one normalized range in the AI section.
- State boundaries such as personal demo vs production, mock tools vs real APIs, preference judging vs factual accuracy, and planned launch vs confirmed production.

### 7. Summarize the session

End every note with:

- `考察重点`: what the interviewer was testing
- `主要问题`: weaknesses grounded in recorded answers
- `改进方向`: concrete preparation or experiment actions

For HR/career questions, cover business direction, team/manager, role ownership, transferable capability, constraints, and controllable next actions rather than relying only on salary, location, trend, or conversion rate.

### 8. Sync online only when requested

- Follow `references/lark-sync.md`.
- Do not install or configure an online connector merely because local notes were organized.
- Check authentication and scopes before discovery or writes.
- Route content to an existing same-session, organization, project, paper, or technical-topic document before creating anything.
- Deduplicate by normalized question and meaning; write only genuinely new or improved blocks.
- Perform writes serially, read back after each write, and verify purple AI provenance.

### 9. Maintain the collection

- Update a master index with recording sessions, note-only sessions, transcription status, and links.
- Update the project summary with runtime, output locations, backup path, exceptions, and documentation rules.
- Keep note filenames stable unless the user explicitly requests renaming.

### 10. Audit before completion

Run:

```text
python scripts/audit_interview_notes.py <notes-dir> --backup-dir <backup-dir> --require-purple-ai
```

Resolve every missing section, unmarked AI answer, missing purple label, hallucination phrase, broken local link, or backup mismatch. When online sync was requested, also report each local note, target document, pre/post revision, inserted or replaced block count, deduplicated question count, and failed or deferred write. Never claim online success from process exit code alone; require a successful result and read-back check.
