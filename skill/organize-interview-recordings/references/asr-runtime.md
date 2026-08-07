# Local ASR Runtime

## Route by operating system and spoken language

Choose from the dominant spoken language, not the requested output language:

| Host | Chinese-dominant | English-dominant |
| --- | --- | --- |
| macOS Apple Silicon | `qwen3-asr-large` / `mlx-qwen3-asr` | `whisper-large` / `mlx_whisper` |
| Windows | `qwen3-asr-large` / bundled `transcribe_qwen_windows.py` | `whisper-large` / bundled `transcribe_whisper_windows.py` |

Allow overrides:

- `QWEN_ASR_COMMAND`: complete path to the Qwen wrapper.
- `WHISPER_ASR_COMMAND`: complete path to the Whisper wrapper.
- `QWEN_ASR_MODEL`: Hugging Face model ID or local model directory.
- `WHISPER_MODEL`: compatible model ID or local model directory.

For setup or repair, read exactly one platform guide:

- Apple Silicon: `references/setup-macos.md`
- Windows or Intel Mac fallback: `references/setup-windows.md`

Do not replace a healthy configured runtime or download another large model without need.

## Dominant-language rule

- Chinese-dominant, including Mandarin with English technical terms: use Qwen3-ASR.
- English-dominant: use Whisper large-v3 with `language=en`.
- Genuinely mixed: route by the language carrying most substantive content.
- Unclear: inspect notes or transcribe one short representative sample. Do not run two complete passes just to decide.

## Health checks

macOS:

```bash
command -v qwen3-asr-large
qwen3-asr-large --version
command -v whisper-large
whisper-large --version
ffmpeg -version
```

Windows PowerShell:

```powershell
Get-Command qwen3-asr-large
qwen3-asr-large --version
Get-Command whisper-large
whisper-large --version
ffmpeg -version
```

If the global wrapper is absent but the platform environment exists, invoke the bundled script with the matching virtual-environment Python. Never assume a user-specific absolute path.

## Chinese transcription

macOS:

```bash
QWEN_ASR_CONTEXT="organization role project technical terms" \
  qwen3-asr-large "/absolute/path/interview.mp4" "/absolute/path/output"
```

Known two-person interview, only when diarization was installed and authorized:

```bash
QWEN_ASR_DIARIZE=True QWEN_ASR_NUM_SPEAKERS=2 \
  qwen3-asr-large "/absolute/path/interview.mp4" "/absolute/path/output"
```

Windows PowerShell:

```powershell
qwen3-asr-large "D:\recordings\interview.mp4" "D:\transcripts\interview"
```

The official Windows backend does not currently use the macOS MLX `QWEN_ASR_CONTEXT` option. Verify proper nouns manually.

## English transcription

macOS:

```bash
WHISPER_LANGUAGE=en \
WHISPER_INITIAL_PROMPT="Organization, people, projects, and technical terms." \
  whisper-large "/absolute/path/interview.mp4" "/absolute/path/output"
```

Windows PowerShell:

```powershell
$env:WHISPER_LANGUAGE = "en"
$env:WHISPER_INITIAL_PROMPT = "Organization, people, projects, and technical terms."
whisper-large "D:\recordings\interview.mp4" "D:\transcripts\interview"
```

Keep the task as transcription. Do not translate when the goal is an English transcript.

## Output contract

For each recording, retain:

- `.txt`: readable raw transcript
- `.srt`: timestamps for manual verification
- `.json`: segments, timestamps, language, model, and available speaker metadata

Use one output directory per recording. Resume from valid outputs rather than overwriting or retranscribing them.

## Quality checks

- Confirm a usable audio stream exists.
- Compare media duration with the final transcript timestamp.
- Inspect first, middle, and final valid segments.
- Check names, dates, metrics, and numbers against audio or source notes.
- Flag extreme repetition, low lexical diversity, dense text over silence, or implausible speaker switching.
- If interviewer audio is weak, reconstruct the question only when intent is clear, and label it as AI reconstruction.
