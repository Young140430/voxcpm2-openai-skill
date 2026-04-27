# VoxCPM2 OpenAI Speech Skill

通过 OpenAI 兼容的 `/v1/audio/speech` 接口将文本转换为语音，支持零样本合成和参考音色克隆。只需有可访问的 vllm_omni API 地址即可使用，无需本地部署模型。

## 前置要求

- Python >= 3.8
- 可访问的 vllm_omni API 地址（通过 `--api-base` 指定，默认 `http://localhost:8000`）
- 首次运行自动安装 `httpx` 依赖

## API 地址

通过 `--api-base` 指定 vllm_omni API 地址，可以是本地或远程服务器：

```bash
# 本地服务器
python voxcpm2_speech.py "你好" --api-base http://localhost:8000

# 远程服务器
python voxcpm2_speech.py "你好" --api-base http://your-server:8000
```

如需自行部署服务器，可参考以下命令：

```bash
vllm serve openbmb/VoxCPM2 --omni --host 0.0.0.0 --port 8000
```

## 安装

无需额外安装步骤，直接运行脚本即可。首次运行会自动安装 Python 依赖。

也可使用安装脚本：

```bash
# Linux/macOS
bash setup.sh

# Windows
setup.bat
```

## 使用

### 零样本合成

```bash
python voxcpm2_speech.py "你好，欢迎使用语音合成"
```

### 指定输出文件

```bash
python voxcpm2_speech.py "Hello world." -o hello.wav
```

### 音色克隆（本地音频文件）

```bash
python voxcpm2_speech.py "今天天气不错" --ref-audio speaker.wav
```

### 音色克隆（URL）

```bash
python voxcpm2_speech.py "今天天气不错" --ref-audio "https://example.com/speaker.wav"
```

### 自定义 API 服务器

```bash
python voxcpm2_speech.py "测试" --api-base http://your-server:8000
```

### 使用 curl 测试

```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "voxcpm2", "input": "Hello, this is VoxCPM2.", "voice": "default", "stream": true}' \
  --output output.wav
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `text` | 要合成的目标文本（必需） | - |
| `-o, --output` | 输出音频文件路径 | `output.wav` |
| `--ref-audio` | 参考音频（本地路径、URL 或 data: URI） | 无 |
| `--model` | 模型名称 | `voxcpm2` |
| `--api-base` | API 服务器地址 | `http://localhost:8000` |
| `--api-key` | API 密钥 | `sk-empty` |
| `--response-format` | 输出音频格式（wav/mp3/flac/ogg） | `wav` |

## `--ref-audio` 支持的格式

- **本地文件路径**：自动编码为 base64 data URI 发送
- **URL**：`https://example.com/speaker.wav`，直接传递给服务器
- **Base64 data URI**：`data:audio/wav;base64,UklGRi...`，直接传递给服务器

## 文件结构

```
voxcpm2-openai-speech/
├── SKILL.md           # Skill 定义文件（AI Agent 读取）
├── README.md          # 本文件
├── voxcpm2_speech.py  # 主脚本（CLI 入口）
├── setup.sh           # Linux/macOS 安装脚本
└── setup.bat          # Windows 安装脚本
```

## 相关链接

- **GitHub**: https://github.com/OpenBMB/VoxCPM
- **ModelScope**: https://www.modelscope.cn/models/OpenBMB/VoxCPM2
