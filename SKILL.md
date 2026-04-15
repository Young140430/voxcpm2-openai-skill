---
name: voxcpm2-openai-speech
description: |
  VoxCPM2 OpenAI 兼容语音合成技能。通过 OpenAI /v1/audio/speech 接口将文本转换为语音，支持零样本合成和参考音色克隆。
  只需有可访问的 vllm_omni API 地址即可使用，无需本地部署模型。兼容 OpenAI TTS API 协议。
  触发条件：用户需要语音合成、TTS、文字转语音、音色克隆、生成语音文件，且使用 OpenAI 兼容接口。
  要求：Python >= 3.8，依赖 httpx，首次运行自动安装。
---

# VoxCPM2 OpenAI Speech — 兼容 OpenAI 接口的语音合成

通过 OpenAI 兼容的 `/v1/audio/speech` 接口将文本转换为语音文件，支持零样本合成和参考音色克隆。只需有可访问的 vllm_omni API 地址即可使用，无需本地部署模型。

## 快速开始

```bash
# 零样本合成
python voxcpm2_speech.py "你好，欢迎使用语音合成"

# 指定输出文件
python voxcpm2_speech.py "Hello world." -o hello.wav

# 使用参考音色克隆（本地音频文件）
python voxcpm2_speech.py "今天天气不错" --ref-audio speaker.wav

# 使用参考音色克隆（URL）
python voxcpm2_speech.py "今天天气不错" --ref-audio "https://example.com/speaker.wav"

# 自定义 API 服务器
python voxcpm2_speech.py "测试" --api-base http://your-server:8000
```

## 命令参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `text` | 要合成的目标文本（必需） | - |
| `-o, --output` | 输出音频文件路径 | `output.wav` |
| `--ref-audio` | 参考音频（本地路径、URL 或 data: URI） | 无 |
| `--model` | 模型名称 | `voxcpm2` |
| `--api-base` | API 服务器地址 | `http://localhost:8000` |
| `--api-key` | API 密钥 | `sk-empty` |
| `--response-format` | 输出音频格式（wav/mp3/flac/ogg） | `wav` |

## 两种合成模式

### 1. 零样本模式（无参考音频）

```bash
python voxcpm2_speech.py "这是零样本合成的语音"
```

- 不提供参考音频，使用模型默认音色
- 适合快速测试

### 2. 音色克隆模式（参考音频）

```bash
# 本地文件（自动编码为 base64）
python voxcpm2_speech.py "用参考音色说这句话" --ref-audio speaker.wav

# URL
python voxcpm2_speech.py "用参考音色说这句话" --ref-audio "https://example.com/speaker.wav"

# Base64 data URI
python voxcpm2_speech.py "用参考音色说这句话" --ref-audio "data:audio/wav;base64,UklGRi..."
```

- 提供参考音频，克隆说话人音色
- 支持本地文件、URL、Base64 data URI 三种格式
- 本地文件自动编码为 base64 data URI 发送

## 工作流程

当用户请求生成语音时，按以下步骤执行：

```python
WORKFLOW = [
    {
        "step": 1,
        "name": "parse_request",
        "tasks": ["提取目标文本", "确定是否需要参考音频", "确定输出文件路径和格式"]
    },
    {
        "step": 2,
        "name": "validate_inputs",
        "tasks": ["检查 Python 版本 >= 3.8", "确认参考音频文件存在（如有）", "确认 API 服务器可达"]
    },
    {
        "step": 3,
        "name": "generate_speech",
        "command": "python voxcpm2_speech.py \"{text}\" --ref-audio {ref_audio} -o {output}",
        "tasks": ["调用 voxcpm2_speech.py 生成语音", "等待生成完成"]
    },
    {
        "step": 4,
        "name": "deliver_result",
        "tasks": ["确认输出文件已生成", "告知用户文件路径"]
    }
]
```

## API 地址

使用 `--api-base` 指定 vllm_omni API 地址，可以是本地或远程服务器：

```bash
# 本地服务器
python voxcpm2_speech.py "你好" --api-base http://localhost:8000

# 远程服务器
python voxcpm2_speech.py "你好" --api-base http://your-server:8000
```

默认 API 地址为 `http://localhost:8000`。如需自行部署服务器，可参考以下命令：

```bash
python -m vllm_omni.entrypoints.openai.api_server \
    --model openbmb/VoxCPM2 \
    --stage-configs-path vllm_omni/model_executor/stage_configs/voxcpm2.yaml \
    --host 0.0.0.0 --port 8000
```

## 故障排除

| 问题 | 解决方案 |
|------|---------|
| `httpx` 缺失 | 首次运行自动安装，或手动 `pip install httpx` |
| 连接超时 | 检查 API 地址是否正确、服务器是否可达 |
| 参考音频编码失败 | 确保音频为 WAV/MP3/FLAC/OGG 格式，文件未损坏 |
| 返回 404 | 确认服务器已加载 VoxCPM2 模型及 stage-configs |
