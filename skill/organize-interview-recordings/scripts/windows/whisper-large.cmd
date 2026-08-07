@echo off
setlocal
if defined INTERVIEW_ASR_ROOT (
  set "RUNTIME_ROOT=%INTERVIEW_ASR_ROOT%"
) else (
  for %%I in ("%~dp0..") do set "RUNTIME_ROOT=%%~fI"
)
"%RUNTIME_ROOT%\whisper\venv\Scripts\python.exe" "%RUNTIME_ROOT%\scripts\transcribe_whisper_windows.py" %*
exit /b %ERRORLEVEL%
