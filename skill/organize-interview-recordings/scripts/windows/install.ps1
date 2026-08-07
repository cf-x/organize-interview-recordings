[CmdletBinding()]
param(
    [switch]$AddToPath,
    [switch]$DownloadModels,
    [string]$TorchIndexUrl = "",
    [string]$RuntimeRoot = ""
)

$ErrorActionPreference = "Stop"

if (-not $RuntimeRoot) {
    $RuntimeRoot = Join-Path $env:LOCALAPPDATA "interview-asr"
}

$PythonLauncher = Get-Command py -ErrorAction SilentlyContinue
if (-not $PythonLauncher) {
    throw "Python launcher 'py' was not found. Install 64-bit Python 3.12 first."
}

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$QwenRoot = Join-Path $RuntimeRoot "qwen"
$WhisperRoot = Join-Path $RuntimeRoot "whisper"
$RuntimeScripts = Join-Path $RuntimeRoot "scripts"
$RuntimeBin = Join-Path $RuntimeRoot "bin"
$QwenPython = Join-Path $QwenRoot "venv\Scripts\python.exe"
$WhisperPython = Join-Path $WhisperRoot "venv\Scripts\python.exe"

New-Item -ItemType Directory -Force -Path $QwenRoot, $WhisperRoot, $RuntimeScripts, $RuntimeBin | Out-Null

& py -3.12 -m venv (Join-Path $QwenRoot "venv")
if ($LASTEXITCODE -ne 0) { throw "Failed to create the Qwen Python environment." }

& py -3.12 -m venv (Join-Path $WhisperRoot "venv")
if ($LASTEXITCODE -ne 0) { throw "Failed to create the Whisper Python environment." }

& $QwenPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Failed to upgrade pip in the Qwen environment." }

if ($TorchIndexUrl) {
    & $QwenPython -m pip install --upgrade torch torchaudio --index-url $TorchIndexUrl
    if ($LASTEXITCODE -ne 0) { throw "Failed to install PyTorch from the selected index." }
}

& $QwenPython -m pip install --upgrade qwen-asr "huggingface_hub[cli]"
if ($LASTEXITCODE -ne 0) { throw "Failed to install qwen-asr." }

& $WhisperPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Failed to upgrade pip in the Whisper environment." }

& $WhisperPython -m pip install --upgrade faster-whisper "huggingface_hub[cli]"
if ($LASTEXITCODE -ne 0) { throw "Failed to install faster-whisper." }

Copy-Item -Force (Join-Path $ScriptRoot "transcribe_qwen_windows.py") $RuntimeScripts
Copy-Item -Force (Join-Path $ScriptRoot "transcribe_whisper_windows.py") $RuntimeScripts
Copy-Item -Force (Join-Path $ScriptRoot "qwen3-asr-large.cmd") $RuntimeBin
Copy-Item -Force (Join-Path $ScriptRoot "whisper-large.cmd") $RuntimeBin

if ($DownloadModels) {
    $QwenHf = Join-Path $QwenRoot "venv\Scripts\hf.exe"
    $WhisperHf = Join-Path $WhisperRoot "venv\Scripts\hf.exe"
    & $QwenHf download Qwen/Qwen3-ASR-1.7B
    if ($LASTEXITCODE -ne 0) { throw "Failed to download Qwen3-ASR-1.7B." }
    & $QwenHf download Qwen/Qwen3-ForcedAligner-0.6B
    if ($LASTEXITCODE -ne 0) { throw "Failed to download Qwen3-ForcedAligner-0.6B." }
    & $WhisperHf download Systran/faster-whisper-large-v3
    if ($LASTEXITCODE -ne 0) { throw "Failed to download faster-whisper-large-v3." }
}

if ($AddToPath) {
    $UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $PathParts = @($UserPath -split ";" | Where-Object { $_ })
    if ($PathParts -notcontains $RuntimeBin) {
        $NewPath = (($PathParts + $RuntimeBin) -join ";")
        [Environment]::SetEnvironmentVariable("Path", $NewPath, "User")
        Write-Host "Added to user PATH: $RuntimeBin"
    }
}

Write-Host "Installed Qwen runtime: $QwenRoot"
Write-Host "Installed Whisper runtime: $WhisperRoot"
Write-Host "Installed wrappers: $RuntimeBin"
Write-Host "Open a new terminal, then run qwen3-asr-large --version and whisper-large --version."
