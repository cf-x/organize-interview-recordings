#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
  echo "This installer requires an Apple Silicon Mac." >&2
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "FFmpeg is required. Install it first with: brew install ffmpeg" >&2
  exit 1
fi

PYTHON_COMMAND="${INTERVIEW_ASR_PYTHON:-python3}"
if ! command -v "${PYTHON_COMMAND}" >/dev/null 2>&1; then
  echo "Python was not found: ${PYTHON_COMMAND}" >&2
  exit 1
fi

RUNTIME_ROOT="${INTERVIEW_ASR_ROOT:-${HOME}/.local/share/interview-asr}"
WRAPPER_DIR="${INTERVIEW_ASR_BIN:-${HOME}/.local/bin}"
QWEN_ENV="${RUNTIME_ROOT}/qwen/venv"
WHISPER_ENV="${RUNTIME_ROOT}/whisper/venv"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "${RUNTIME_ROOT}/qwen" "${RUNTIME_ROOT}/whisper" "${WRAPPER_DIR}"

"${PYTHON_COMMAND}" -m venv "${QWEN_ENV}"
"${PYTHON_COMMAND}" -m venv "${WHISPER_ENV}"

"${QWEN_ENV}/bin/python" -m pip install --upgrade pip
if [[ "${INSTALL_DIARIZATION:-0}" == "1" ]]; then
  "${QWEN_ENV}/bin/python" -m pip install --upgrade "mlx-qwen3-asr[aligner,diarize]" "huggingface_hub[cli]"
else
  "${QWEN_ENV}/bin/python" -m pip install --upgrade "mlx-qwen3-asr[aligner]" "huggingface_hub[cli]"
fi

"${WHISPER_ENV}/bin/python" -m pip install --upgrade pip
"${WHISPER_ENV}/bin/python" -m pip install --upgrade mlx-whisper "huggingface_hub[cli]"

install -m 0755 "${SCRIPT_DIR}/qwen3-asr-large" "${WRAPPER_DIR}/qwen3-asr-large"
install -m 0755 "${SCRIPT_DIR}/whisper-large" "${WRAPPER_DIR}/whisper-large"

if [[ "${DOWNLOAD_MODELS:-0}" == "1" ]]; then
  "${QWEN_ENV}/bin/hf" download Qwen/Qwen3-ASR-1.7B
  "${QWEN_ENV}/bin/hf" download Qwen/Qwen3-ForcedAligner-0.6B
  "${WHISPER_ENV}/bin/hf" download mlx-community/whisper-large-v3-mlx
fi

echo "Installed Qwen runtime: ${QWEN_ENV}"
echo "Installed Whisper runtime: ${WHISPER_ENV}"
echo "Installed wrappers: ${WRAPPER_DIR}"
echo "Add ${WRAPPER_DIR} to PATH, then run qwen3-asr-large --version and whisper-large --version."
