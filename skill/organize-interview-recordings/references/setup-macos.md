# macOS Apple Silicon Setup

This route uses MLX and targets M-series Macs. It keeps Qwen and Whisper in separate virtual environments to reduce dependency conflicts.

## Requirements

- Apple Silicon Mac; MLX does not support Intel Mac.
- Python 3.10–3.13.
- Homebrew and FFmpeg.
- At least 16 GB unified memory; 24 GB or more is recommended for Qwen3-ASR-1.7B plus timestamp alignment.
- At least 15 GB free disk space for environments and model caches.

## Install

From the Skill directory:

```bash
brew install ffmpeg
bash scripts/macos/install.sh
```

The default runtime root is `${HOME}/.local/share/interview-asr`; wrappers are copied to `${HOME}/.local/bin`. Override the root with `INTERVIEW_ASR_ROOT` before installation and execution.

Add the wrapper directory to the shell PATH if needed:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Install optional diarization dependencies:

```bash
INSTALL_DIARIZATION=1 bash scripts/macos/install.sh
```

Diarization requires accepting the selected pyannote model terms and authenticating with a read-only Hugging Face token. Never put the token in scripts, notes, shell history, or Git.

## Download models

First use downloads models automatically. To pre-download all default weights:

```bash
DOWNLOAD_MODELS=1 bash scripts/macos/install.sh
```

Or download individually:

```bash
${HOME}/.local/share/interview-asr/qwen/venv/bin/hf download Qwen/Qwen3-ASR-1.7B
${HOME}/.local/share/interview-asr/qwen/venv/bin/hf download Qwen/Qwen3-ForcedAligner-0.6B
${HOME}/.local/share/interview-asr/whisper/venv/bin/hf download mlx-community/whisper-large-v3-mlx
```

Set `HF_HOME` before installation and execution to move the shared Hugging Face cache:

```bash
export HF_HOME="/path/to/model-cache"
```

## Run

Chinese:

```bash
QWEN_ASR_CONTEXT="known names and terms" \
  qwen3-asr-large "/path/interview.mp4" "/path/output"
```

English:

```bash
WHISPER_LANGUAGE=en \
WHISPER_INITIAL_PROMPT="Known names and terms." \
  whisper-large "/path/interview.mp4" "/path/output"
```

Both wrappers generate a new timestamped output directory when an output path is omitted. Explicitly specifying the same output directory may overwrite files with the same names, so prefer one directory per recording.

## Smaller model and low-memory mode

Use the Qwen 0.6B model when 1.7B does not fit comfortably:

```bash
QWEN_ASR_MODEL="Qwen/Qwen3-ASR-0.6B" qwen3-asr-large "/path/interview.mp4"
```

Skip the forced aligner when only plain text is required:

```bash
QWEN_ASR_TIMESTAMPS=False QWEN_ASR_OUTPUT_FORMAT=txt \
  qwen3-asr-large "/path/interview.mp4"
```

## Verify and repair

```bash
qwen3-asr-large --version
qwen3-asr-large --doctor
whisper-large --version
ffmpeg -version
```

Rerunning `scripts/macos/install.sh` repairs packages without deleting the shared model cache. Do not remove the cache merely to repair a Python environment.

## Implementation notes

- `mlx-qwen3-asr` is a community MLX implementation; the model weights come from Qwen.
- `mlx-whisper` accepts MLX-format Whisper repositories and downloads them from Hugging Face when needed.
- Network access is needed for initial package/model download. Cached inference stays local.

Upstream references:

- https://github.com/QwenLM/Qwen3-ASR
- https://github.com/moona3k/mlx-qwen3-asr
- https://github.com/ml-explore/mlx-examples/tree/main/whisper
