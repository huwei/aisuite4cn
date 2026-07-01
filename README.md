# aisuite4cn

[![PyPI](https://img.shields.io/pypi/v/aisuite4cn)](https://pypi.org/project/aisuite4cn/)

简单、统一的接口，可连接多个中国生成式人工智能提供商。

`aisuite4cn` 是一个 Python 客户端库，为中国的各类大模型厂商提供统一的 OpenAI 兼容接口。学习了 [aisuite](https://github.com/andrewyng/aisuite) 方案并进行了扩展，支持 **Chat Completions API** 和 **Responses API** 双协议，使得开发者无需更改代码即可在不同 LLM 之间无缝切换。

## 安装

```shell
pip install aisuite4cn
```

安装特定提供商：

```shell
pip install 'aisuite4cn[qwen]'
```

安装所有提供商：

```shell
pip install 'aisuite4cn[all]'
```

## API 协议

`aisuite4cn` 支持三种 API：

| API | 调用方式 | 说明 |
|-----|---------|------|
| **Chat Completions** | `client.chat.completions.create()` | 标准对话补全接口，所有提供商均原生支持 |
| **Responses API** | `client.responses.create()` | OpenAI 新一代 Responses 接口，部分提供商原生支持，其余通过内部转换自动适配 |
| **Embeddings** | `client.embeddings.create()` | 文本向量化接口 |

同步与异步均支持：

```python
import aisuite4cn as ai

client = ai.Client()          # 同步
client = ai.AsyncClient()     # 异步
```

## 支持的提供商与模型

模型名称格式：`<provider>:<model-name>`（如 `qwen:qwen-max`）

### 协议支持总览

| 提供商 | Chat Completions | Responses API | 示例模型 | 必需环境变量 |
|--------|:---:|:---:|----------|-------------|
| `qwen` | ✅ 原生 | ✅ 原生 | `qwen-max` | `DASHSCOPE_API_KEY` |
| `dashscope` | ✅ 原生 | ✅ 原生 | `qwen-max` | `DASHSCOPE_API_KEY` |
| `dmxapi` | ✅ 原生 | ✅ 原生 | `gemini-2.5-flash` | `DMXAPI_API_KEY` |
| `hermes_agent` | ✅ 原生 | ✅ 原生 | `deepseek-v4-pro` | `HERMES_AGENT_BASE_URL`, `HERMES_AGENT_API_KEY` |
| `custom` | ✅ 原生 | ✅ 原生 | 用户自定义 | `CUSTOM_BASE_URL`, `CUSTOM_API_KEY` |
| `openclaw` | ✅ 原生 | ✅ 原生 | 用户自定义 | `OPENCLAW_BASE_URL`, `OPENCLAW_API_KEY` |
| `ark` | ✅ 原生 | 🔄 转换 | `doubao-seed-1.6-250615` | `ARK_API_KEY` |
| `deepseek` | ✅ 原生 | 🔄 转换 | `deepseek-chat` | `DEEPSEEK_API_KEY` |
| `moonshot` | ✅ 原生 | 🔄 转换 | `moonshot-v1-8k` | `MOONSHOT_API_KEY` |
| `qianfan` | ✅ 原生 | 🔄 转换 | `ernie-3.5-8k` | `QIANFAN_ACCESS_KEY`, `QIANFAN_SECRET_KEY` |
| `zhipuai` | ✅ 原生 | 🔄 转换 | `glm-4-flash` | `ZHIPUAI_API_KEY` |
| `baichuan` | ✅ 原生 | 🔄 转换 | `Baichuan4` | `BAICHUAN_API_KEY` |
| `spark` | ✅ 原生 | 🔄 转换 | `4.0Ultra` | `SPARK_API_KEY_MAP` |
| `iflytek` | ✅ 原生 | 🔄 转换 | `spark-v3.5` | `IFLYTEK_API_KEY` |
| `stepfun` | ✅ 原生 | 🔄 转换 | `step-v1` | `STEP_API_KEY` |
| `minimax` | ✅ 原生 | 🔄 转换 | `MiniMax-M2` | `MINIMAX_API_KEY` |
| `hunyuan` | ✅ 原生 | 🔄 转换 | `hunyuan-standard` | `HUNYUAN_API_KEY` |
| `ollama` | ✅ 原生 | 🔄 转换 | `qwen3:30b` | `OLLAMA_BASE_URL` |
| `siliconflow` | ✅ 原生 | 🔄 转换 | `BAAI/bge-m3` | `SILICONFLOW_API_KEY` |
| `siliconrouter` | ✅ 原生 | 🔄 转换 | — | `SILICONROUTER_API_KEY` |
| `mimo` | ✅ 原生 | 🔄 转换 | — | `MIMO_API_KEY` |
| `xiaomi` | ✅ 原生 | 🔄 转换 | — | `MIMO_API_KEY` |
| `yunwu` | ✅ 原生 | 🔄 转换 | `deepseek-chat` | `YUNWU_API_KEY` |
| `longcat` | ✅ 原生 | 🔄 转换 | `LongCat-Flash-Chat` | `LONGCAT_API_KEY` |

> **图例**：✅ 原生 = 后端服务直接支持该协议；🔄 转换 = 请求在内部自动从 Responses 格式转换为 Chat Completions 格式调用，结果再转换回 Responses 格式返回，无需用户做任何适配。

### 特殊配置说明

| 提供商 | 说明 |
|--------|------|
| `dashscope` | `qwen` 的别名，使用相同的 API 端点 |
| `xiaomi` | `mimo` 的别名，使用相同的 API 端点 |
| `spark` | 使用模型到密钥的映射，通过 `SPARK_API_KEY_MAP` 配置（格式：`model=key&model=key`） |
| `qianfan` | 使用百度 IAM 认证，需要 Access Key + Secret Key（非普通 API Key） |
| `ollama` | 本地部署，需设置 `OLLAMA_BASE_URL`（如 `http://localhost:11434/v1`） |
| `hermes_agent` | 需设置 `HERMES_AGENT_BASE_URL` 指向代理服务地址 |
| `custom` | 自定义 OpenAI 兼容接口，需设置 `CUSTOM_BASE_URL` 和 `CUSTOM_API_KEY` |

## 配置

### 方式一：环境变量

```shell
# Qwen / Dashscope（阿里云千问 / 百炼）
export DASHSCOPE_API_KEY="your-dashscope-api-key"

# Ark / Doubao（火山引擎方舟）
export ARK_API_KEY="your-ark-api-key"

# DeepSeek（深度求索）
export DEEPSEEK_API_KEY="your-deepseek-api-key"

# Moonshot（月之暗面）
export MOONSHOT_API_KEY="your-moonshot-api-key"

# ZhipuAI（智谱AI）
export ZHIPUAI_API_KEY="your-zhipuai-api-key"

# Qianfan（百度千帆 / 文心一言）— IAM 认证
export QIANFAN_ACCESS_KEY="your-qianfan-access-key"
export QIANFAN_SECRET_KEY="your-qianfan-secret-key"

# Baichuan（百川智能）
export BAICHUAN_API_KEY="your-baichuan-api-key"

# Spark（讯飞星火，按模型名映射密钥）
export SPARK_API_KEY_MAP="4.0Ultra=your-key&generalv3=your-key"

# iFlytek（讯飞星火 x2）
export IFLYTEK_API_KEY="your-iflytek-api-key"

# Hunyuan（腾讯混元）
export HUNYUAN_API_KEY="your-hunyuan-api-key"

# Minimax
export MINIMAX_API_KEY="your-minimax-api-key"

# Stepfun（阶跃星辰）
export STEP_API_KEY="your-step-api-key"

# Siliconflow（硅基流动）
export SILICONFLOW_API_KEY="your-siliconflow-api-key"

# SiliconRouter
export SILICONROUTER_API_KEY="your-siliconrouter-api-key"

# DMXAPI（多模态 API 聚合平台）
export DMXAPI_API_KEY="your-dmxapi-api-key"

# Mimo / Xiaomi（小米 MiMo）
export MIMO_API_KEY="your-mimo-api-key"

# Longcat（美团 Longcat）
export LONGCAT_API_KEY="your-longcat-api-key"

# Yunwu（云雾）
export YUNWU_API_KEY="your-yunwu-api-key"

# Hermes Agent（代理服务）
export HERMES_AGENT_BASE_URL="your-hermes-agent-base-url"
export HERMES_AGENT_API_KEY="your-hermes-agent-api-key"

# Ollama（本地部署）
export OLLAMA_BASE_URL="http://localhost:11434/v1"

# OpenClaw
export OPENCLAW_BASE_URL="your-openclaw-base-url"
export OPENCLAW_API_KEY="your-openclaw-api-key"

# Custom（自定义 OpenAI 兼容接口）
export CUSTOM_BASE_URL="your-custom-base-url"
export CUSTOM_API_KEY="your-custom-api-key"
```

### 方式二：`provider_configs` 参数

```python
import aisuite4cn as ai

client = ai.Client(provider_configs={
    "qwen": {"api_key": "your-dashscope-api-key"},
    "moonshot": {"api_key": "your-moonshot-api-key"},
    "deepseek": {"api_key": "your-deepseek-api-key"},
    "ark": {"api_key": "your-ark-api-key"},
    "ollama": {"base_url": "http://localhost:11434/v1"},
    "custom": {"base_url": "your-custom-base-url", "api_key": "your-custom-api-key"},
})
```

> 通过 `provider_configs` 传入的配置优先级高于环境变量。

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="qwen:qwen-max",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ],
    temperature=0.75
)
print(response.choices[0].message.content)
```

### Responses API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.responses.create(
    model="qwen:qwen-max",
    input="Hello!",
    instructions="You are a helpful assistant.",
)
print(response.output[0].content[0].text)
```

> 所有提供商均可通过 `responses.create()` 调用。原生支持的提供商直接转发到后端，其余提供商在内部自动完成协议转换。

### 多模型对比

```python
import aisuite4cn as ai

client = ai.Client()

models = [
    "deepseek:deepseek-chat",
    "moonshot:moonshot-v1-8k",
    "qwen:qwen-max",
    "zhipuai:glm-4-flash",
    "hunyuan:hunyuan-standard",
    "qianfan:ernie-3.5-8k",
    "spark:4.0Ultra",
    "minimax:MiniMax-M2",
    "longcat:LongCat-Flash-Chat",
]

messages = [
    {"role": "system", "content": "Respond in Pirate English."},
    {"role": "user", "content": "Tell me a joke."},
]

for model in models:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.75
    )
    print(f"\n--- {model} ---")
    print(response.choices[0].message.content)
```

## 协议转换机制

对于不支持 Responses API 的提供商，`aisuite4cn` 在内部自动完成以下转换：

- **输入转换**：将 Responses API 的 `input`（字符串或类型化列表）+ `instructions` 转换为 Chat Completions 的 `messages` 格式
- **参数映射**：`max_output_tokens` → `max_tokens`，其余通用参数（`temperature`、`top_p`、`stop` 等）直接透传，不兼容参数自动过滤
- **输出转换**：将 Chat Completions 的 `ChatCompletion` 响应转换为 Responses API 的 `Response` 对象，包括推理内容（reasoning）、工具调用（tool_calls）、用量统计（usage）
- **流式转换**：将 Chat Completions 的 `ChatCompletionChunk` 流转换为 Responses API 的 `ResponseStreamEvent` 事件序列

这一机制对用户完全透明，使用 `responses.create()` 时无需关心底层提供商是否原生支持。

## License

`aisuite4cn` 在 MIT 许可证下发布。您可以自由地将代码用于商业和非商业目的。

## 致谢

### aisuite
https://github.com/andrewyng/aisuite

### openai-python
https://github.com/openai/openai-python

## Development Guide
Please refer to [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development and installation instructions.
