# Local ASR Runtime

## Route by operating system and spoken language

Choose from the dominant spoken language, not the requested output language:

| Host | Chinese-dominant | English-dominant |
| --- | --- | --- |
| macOS Apple Silicon | `qwen3-asr-large` / `mlx-qwen3-asr` | `whisper-large` / `mlx_whisper` |
| Windows | `qwen3-asr-large` / bundled `transcribe_qwen_windows.py` | `whisper-large` / bundled `transcribe_whisper_windows.py` |

Resolve executable paths in this order: an explicit user choice, the environment overrides below, the matching key in the private `local-settings.json`, then the platform defaults. Treat values as executable paths, never shell snippets. Check executability before running.

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

## Source-separated MP4 recordings

Inspect every MP4/MOV before choosing diarization. QuietRecorder recordings created with the source-separated layout contain three AAC tracks in this order and with these titles:

1. `mixed`: default playback track containing both sources
2. `system`: system playback, normally the remote interviewer group
3. `microphone`: local built-in microphone, normally the candidate

Use `ffprobe` to inspect audio-stream count, order, channel counts, default disposition, start times, and durations. QuietRecorder writes AVFoundation track titles, although `ffprobe` may not expose those ISO track-title atoms. Treat the layout as validated when the MP4 has three AAC audio streams—default stereo, non-default stereo, non-default mono—and the adjacent telemetry contains `audioTrackLayout: ["mixed", "system", "microphone"]`. If the reader exposes titles, use them as an additional check. Without the telemetry or readable titles, leave the sources unresolved rather than guessing from order or channel count alone.

The current global ASR commands do not expose an audio-stream selector. Passing a multi-track MP4 directly selects one audio stream and loses the source separation. For a validated QuietRecorder layout:

1. Create a temporary directory with `mktemp -d` outside the recording directory.
2. Extract `system` and `microphone` to separate mono 16 kHz PCM WAV files. For the validated QuietRecorder layout, select `0:a:1` and `0:a:2`; these are audio-stream-relative indexes, not absolute file stream indexes. Use `aresample=async=1:first_pts=0` so both files retain the recording's zero-based timeline, including leading silence.
3. Transcribe both WAV files with the language-routed global command and diarization disabled. Use separate output directories named `system` and `microphone`.
4. Add fixed source labels to the JSON segments and merge the two segment lists by start time. Retain overlaps rather than forcing alternating turns. Map `microphone` to `候选人` and `system` to `面试官` only for a remote interview where that mapping is supported by the recording context.
5. Keep the role-specific TXT/SRT/JSON and the merged timestamped transcript. After validating those outputs, remove only the temporary extracted WAV files and directory; keep the source MP4 and all transcript outputs.

Example extraction commands after validating the layout:

```bash
ffmpeg -v error -i "/absolute/path/interview.mp4" \
  -map '0:a:1' -af 'aresample=async=1:first_pts=0' \
  -ar 16000 -ac 1 -c:a pcm_s16le "/temporary/path/system.wav"

ffmpeg -v error -i "/absolute/path/interview.mp4" \
  -map '0:a:2' -af 'aresample=async=1:first_pts=0' \
  -ar 16000 -ac 1 -c:a pcm_s16le "/temporary/path/microphone.wav"
```

Do not transcribe `mixed` when both source tracks are usable. Use it as a fallback when one source track is missing, silent, corrupt, or too contaminated to recover. If several remote interviewers share `system` and distinguishing them is useful, run diarization only on the extracted system WAV. In-person interviews recorded entirely through the microphone and legacy mixed-only files continue to use the conditional diarization workflow.


Use `scripts/merge_transcripts.py` to merge timestamped source JSON into TXT/SRT/JSON without regenerating per-session code. Source roles must be confirmed explicitly. The helper never removes overlapping speech or infers speaker identity. Zero-duration units are flagged for review; do not describe them as precise word alignment. Keep cleaned text separate from raw output.
