# Organize Interview Recordings

一个面向 Codex/Agent 的本地面试录音整理 Skill：按语音主导语言调用本机 ASR，将录屏、录音和原始笔记整理成可复习的结构化问答，同时严格区分录音事实、原始笔记、AI 重建和 AI 优化建议。

> 默认不上传音视频，不附带任何模型权重，也不包含作者的录音、简历、公司资料、账号、令牌或本机绝对路径。

## 能做什么

- 批量盘点 MP4、MKV、MOV、M4A、WAV、现有转写和面试笔记。
- 中文主导语音优先使用 `Qwen/Qwen3-ASR-1.7B`；英文主导语音优先使用 Whisper `large-v3`。
- 保留 TXT、SRT 和结构化 JSON，便于回听和核验。
- 去除问候、重复追问、口头填充和常见 ASR 幻觉，只保留值得复习的问题。
- 将“我的真实回答”和“AI 补充的更好回答”分开，所有推测都带可见来源标记。
- 在改写前备份原笔记，并用审计脚本检查缺失章节、AI 标记、噪声、链接和备份完整性。
- 可选：在本机已经配置兼容的飞书工具时，增量同步新内容；纯本地流程不依赖飞书。
- 将跨场重复问题按考察能力做语义去重，沉淀到项目、技术、代码和 HR 等本地题库。

## 平台与 ASR 路线

| 平台 | 中文主导 | 英文主导 |
| --- | --- | --- |
| macOS Apple Silicon | `mlx-qwen3-asr` + Qwen3-ASR-1.7B | `mlx-whisper` + MLX Whisper large-v3 |
| Windows 10/11 | 官方 `qwen-asr`（NVIDIA CUDA 推荐，CPU 可回退） | `faster-whisper`（CUDA 或 CPU） |

macOS Intel 不支持 MLX。Intel Mac 请采用 Windows 文档中的通用 PyTorch / faster-whisper 路线，并将设备设置为 CPU；长录音会明显更慢。

## 安装 Skill

1. 克隆或下载本仓库。
2. 将 `skill/organize-interview-recordings` 整个目录复制到你的 Skill 目录：

   - Codex：`~/.codex/skills/organize-interview-recordings`
   - 兼容的 Agent 环境：使用该产品约定的个人 Skill 目录

3. 重新打开 Codex/Agent，在提示词中使用：

```text
Use $organize-interview-recordings to organize the interview recordings in <目录>.
```

只想阅读或改造工作流时，不需要安装 ASR。需要实际转写时，再按对应平台配置本地运行时。

## macOS Apple Silicon 流程

要求：Apple Silicon、Python 3.10–3.13、Homebrew、FFmpeg，以及建议至少 16 GB 统一内存；1.7B 模型和时间戳模型同时加载时，24 GB 或以上更从容。

```bash
brew install ffmpeg
cd skill/organize-interview-recordings
bash scripts/macos/install.sh
```

安装脚本会建立两个隔离环境，并把通用命令复制到 `~/.local/bin`：

```bash
export PATH="$HOME/.local/bin:$PATH"
qwen3-asr-large --version
whisper-large --version
```

转写中文面试：

```bash
QWEN_ASR_CONTEXT="产品名 项目名 技术词" \
  qwen3-asr-large "/path/to/interview.mp4" "/path/to/output"
```

转写英文面试：

```bash
WHISPER_LANGUAGE=en \
WHISPER_INITIAL_PROMPT="Product, project, and technical terms." \
  whisper-large "/path/to/interview.mp4" "/path/to/output"
```

完整说明见 [macOS 安装与运行](skill/organize-interview-recordings/references/setup-macos.md)。

## Windows 10/11 流程

要求：64 位 Python 3.12、PowerShell 5.1+；建议安装 FFmpeg。Qwen3-ASR-1.7B 强烈建议使用有足够显存的 NVIDIA GPU。没有 NVIDIA GPU 时可以使用 CPU，但应预期明显更慢，并优先尝试 0.6B 型号。

在 PowerShell 中：

```powershell
cd .\skill\organize-interview-recordings
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\windows\install.ps1
```

脚本默认安装到 `%LOCALAPPDATA%\interview-asr`。打开新终端后：

```powershell
qwen3-asr-large "D:\recordings\interview.mp4" "D:\transcripts\interview"
whisper-large "D:\recordings\interview.mp4" "D:\transcripts\interview-en"
```

如果没有把命令目录加入 PATH，也可以直接运行：

```powershell
& "$env:LOCALAPPDATA\interview-asr\bin\qwen3-asr-large.cmd" --help
& "$env:LOCALAPPDATA\interview-asr\bin\whisper-large.cmd" --help
```

完整的 CUDA、CPU 回退和故障排查见 [Windows 安装与运行](skill/organize-interview-recordings/references/setup-windows.md)。

## ASR 模型下载

运行时会在第一次加载时自动下载模型。若想提前下载、离线转写或明确缓存位置，可使用 Hugging Face CLI。以下命令只下载权重，不会上传录音。

### macOS

```bash
~/.local/share/interview-asr/qwen/venv/bin/hf download Qwen/Qwen3-ASR-1.7B
~/.local/share/interview-asr/qwen/venv/bin/hf download Qwen/Qwen3-ForcedAligner-0.6B
~/.local/share/interview-asr/whisper/venv/bin/hf download mlx-community/whisper-large-v3-mlx
```

也可在安装时一次下载：

```bash
DOWNLOAD_MODELS=1 bash scripts/macos/install.sh
```

### Windows

```powershell
& "$env:LOCALAPPDATA\interview-asr\qwen\venv\Scripts\hf.exe" download Qwen/Qwen3-ASR-1.7B
& "$env:LOCALAPPDATA\interview-asr\qwen\venv\Scripts\hf.exe" download Qwen/Qwen3-ForcedAligner-0.6B
& "$env:LOCALAPPDATA\interview-asr\whisper\venv\Scripts\hf.exe" download Systran/faster-whisper-large-v3
```

中国大陆网络也可以按 Qwen 官方模型卡使用 ModelScope 下载 Qwen 权重：

```bash
pip install -U modelscope
modelscope download --model Qwen/Qwen3-ASR-1.7B --local_dir ./Qwen3-ASR-1.7B
modelscope download --model Qwen/Qwen3-ForcedAligner-0.6B --local_dir ./Qwen3-ForcedAligner-0.6B
```

将本地模型目录赋给 `QWEN_ASR_MODEL` 或相应命令的 `--model` 参数即可。模型会缓存到 Hugging Face/ModelScope 的用户缓存目录；不要把权重提交到本仓库。建议为虚拟环境、Qwen 主模型、时间戳模型和 Whisper 模型合计预留至少 15 GB 磁盘空间。

官方资料：

- [Qwen3-ASR 官方仓库](https://github.com/QwenLM/Qwen3-ASR)
- [Qwen3-ASR-1.7B 模型卡](https://huggingface.co/Qwen/Qwen3-ASR-1.7B)
- [MLX Qwen3-ASR（Apple Silicon 社区实现）](https://github.com/moona3k/mlx-qwen3-asr)
- [MLX Whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)

## 推荐工作流

1. 盘点录音、原笔记、已有 TXT/SRT/JSON 和可用于核验的项目资料。
2. 建立“日期 + 公司/组织 + 轮次”的对应关系。
3. 在时间戳备份目录中复制所有待改写笔记，并核对数量与文件名。
4. 按语音主导语言转写，保留原始输出，不覆盖有效结果。
5. 合并重复追问，保留真实回答的缺点，把修正放进紫色 AI 区域。
6. 每场补齐“考察重点、主要问题、改进方向”。
7. 运行审计：

```bash
python skill/organize-interview-recordings/scripts/audit_interview_notes.py /path/to/notes \
  --backup-dir /path/to/backup \
  --require-purple-ai
```

Windows：

```powershell
python .\skill\organize-interview-recordings\scripts\audit_interview_notes.py D:\notes `
  --backup-dir D:\notes-backup `
  --require-purple-ai
```

## 隐私与脱敏

公开仓库已移除原始版本中的用户目录、项目路径、公司名、个人设备信息和本机模型缓存信息。使用时仍应遵守：

- 不要提交录音、录像、简历、面试笔记、转写、备份或模型权重。
- 不要把 Hugging Face/飞书令牌、Cookie、二维码、授权 URL 或 `.env` 提交到 Git。
- 对外分享笔记前，替换姓名、邮箱、电话、公司内部项目、精确业务指标和未公开面试题。
- 模型下载需要联网；权重缓存完成后，默认转写在本机完成。
- AI 生成的回答、推测范围和重建问题必须明确标记，不能冒充录音原话或公司日志。

仓库的 `.gitignore` 已屏蔽常见音视频、转写、备份、模型和凭据文件，但它不是完整的数据防泄漏系统。发布前仍需人工检查 `git diff --cached`。

## 输出约定

每场笔记至少包含：

- `基本信息`
- `问答记录`
- `面试总结`
- 录音事实或原笔记：普通文本
- AI 优化、估算和重建：紫色来源标签

完整模板见 [输出标准](skill/organize-interview-recordings/references/output-standard.md)。

## 许可

本仓库代码和文档采用 [MIT License](LICENSE)。模型权重、运行库和可选服务各自遵循上游许可证与使用条款；本仓库不重新分发它们。
