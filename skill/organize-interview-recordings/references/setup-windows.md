# Windows Setup

This route uses the official Qwen `qwen-asr` package for Chinese-dominant recordings and `faster-whisper` for English-dominant recordings. It targets Windows 10/11 with 64-bit Python.

## Requirements

- Python 3.12 installed from python.org or Conda. The commands below assume the `py` launcher is available.
- PowerShell 5.1 or later.
- FFmpeg available on PATH for media inspection and broad container support.
- NVIDIA GPU recommended for Qwen3-ASR-1.7B. CPU works as a compatibility fallback but is much slower.
- At least 15 GB free disk space for environments and model caches.

Install FFmpeg with one of these package managers, then open a new terminal:

```powershell
winget install --id Gyan.FFmpeg --exact
```

or:

```powershell
choco install ffmpeg
```

## Install

From the Skill directory:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\windows\install.ps1
```

The default runtime root is `%LOCALAPPDATA%\interview-asr`. The installer creates separate Qwen and Whisper environments and copies wrappers into `%LOCALAPPDATA%\interview-asr\bin`.

To add that directory to the user PATH during installation:

```powershell
.\scripts\windows\install.ps1 -AddToPath
```

Close and reopen the terminal after a PATH change.

## NVIDIA CUDA

Install a PyTorch build compatible with the installed NVIDIA driver before running the installer, or pass the official PyTorch wheel index URL selected for the machine:

```powershell
.\scripts\windows\install.ps1 -TorchIndexUrl "https://download.pytorch.org/whl/cu128"
```

CUDA versions change; use the current selector at https://pytorch.org/get-started/locally/ rather than copying an index URL from another machine. `faster-whisper` also requires compatible NVIDIA runtime libraries for GPU inference. Its official README documents the currently supported CUDA/cuDNN combination.

Without CUDA, omit `-TorchIndexUrl`. The wrapper selects CPU and float32/int8 automatically.

## Download models

Models download automatically on first use. Pre-download them with:

```powershell
& "$env:LOCALAPPDATA\interview-asr\qwen\venv\Scripts\hf.exe" download Qwen/Qwen3-ASR-1.7B
& "$env:LOCALAPPDATA\interview-asr\qwen\venv\Scripts\hf.exe" download Qwen/Qwen3-ForcedAligner-0.6B
& "$env:LOCALAPPDATA\interview-asr\whisper\venv\Scripts\hf.exe" download Systran/faster-whisper-large-v3
```

Or ask the installer to do this:

```powershell
.\scripts\windows\install.ps1 -DownloadModels
```

Set `HF_HOME` before installation and execution to move the shared cache:

```powershell
$env:HF_HOME = "D:\model-cache\huggingface"
```

For Qwen models in mainland China, ModelScope is an official alternative:

```powershell
python -m pip install -U modelscope
modelscope download --model Qwen/Qwen3-ASR-1.7B --local_dir D:\models\Qwen3-ASR-1.7B
modelscope download --model Qwen/Qwen3-ForcedAligner-0.6B --local_dir D:\models\Qwen3-ForcedAligner-0.6B
$env:QWEN_ASR_MODEL = "D:\models\Qwen3-ASR-1.7B"
$env:QWEN_ALIGNER_MODEL = "D:\models\Qwen3-ForcedAligner-0.6B"
```

## Run

Chinese:

```powershell
qwen3-asr-large "D:\recordings\interview.mp4" "D:\transcripts\interview"
```

English:

```powershell
$env:WHISPER_LANGUAGE = "en"
$env:WHISPER_INITIAL_PROMPT = "Known organization, project, and technical terms."
whisper-large "D:\recordings\interview.mp4" "D:\transcripts\interview"
```

Both commands generate `.txt`, `.srt`, and `.json`. The Qwen wrapper uses the forced aligner for timestamps by default. Disable it when only plain text is required:

```powershell
qwen3-asr-large --no-timestamps "D:\recordings\interview.mp4" "D:\transcripts\interview"
```

## Low-memory and CPU fallback

Qwen 0.6B:

```powershell
$env:QWEN_ASR_MODEL = "Qwen/Qwen3-ASR-0.6B"
qwen3-asr-large "D:\recordings\interview.mp4"
```

Force CPU:

```powershell
qwen3-asr-large --device cpu "D:\recordings\interview.mp4"
whisper-large --device cpu --compute-type int8 "D:\recordings\english.mp4"
```

## Verify and repair

```powershell
qwen3-asr-large --version
whisper-large --version
ffmpeg -version
nvidia-smi
```

Rerun `install.ps1` to repair Python packages. Model caches are outside the virtual environments and should not be deleted for ordinary environment repair.

Upstream references:

- https://github.com/QwenLM/Qwen3-ASR
- https://huggingface.co/Qwen/Qwen3-ASR-1.7B
- https://github.com/SYSTRAN/faster-whisper
- https://pytorch.org/get-started/locally/
