# aisuite4cn

[![PyPI](https://img.shields.io/pypi/v/aisuite4cn)](https://pypi.org/project/aisuite4cn/)

简单、统一的接口，可连接多个生成式人工智能提供商。

`aisuite4cn` 针对于中国的各类大模型厂商提供通用的支持。学习了`aisuite`方案，并开发了该库。

`aisuite4cn` 使得开发者能够通过标准化的接口轻松使用多个大型语言模型（LLM）。使用类似于OpenAI的接口，`aisuite4cn` 使得与最受欢迎的LLM互动并比较结果变得简单。它是Python客户端库的轻量级包装器，允许创造者在不改变代码的情况下无缝切换并测试来自不同LLM提供商的响应。我们将在不久的将来扩展它以覆盖更多的用例。

当前支持的提供商和模型如下表所示，模型名称格式为 `<provider>:<model-name>`：

| 提供商 (Provider) | 说明 | 示例模型 | 调用示例 |
|---|---|---|---|
| `moonshot` | 月之暗面 | `moonshot-v1-8k` | `moonshot:moonshot-v1-8k` |
| `ark` | 火山引擎方舟 (Doubao) | `doubao-seed-1.6-250615` | `ark:doubao-seed-1.6-250615` |
| `qwen` | 阿里云千问 | `qwen-max` | `qwen:qwen-max` |
| `dashscope` | 阿里云百炼 (同qwen) | `qwen-max` | `dashscope:qwen-max` |
| `hunyuan` | 腾讯混元 | `hunyuan-standard` | `hunyuan:hunyuan-standard` |
| `qianfan` | 百度文心一言 (Ernie) | `ernie-3.5-8k` | `qianfan:ernie-3.5-8k` |
| `zhipuai` | 智谱AI (ChatGLM) | `glm-4-flash` | `zhipuai:glm-4-flash` |
| `deepseek` | 深度求索 | `deepseek-chat` | `deepseek:deepseek-chat` |
| `baichuan` | 百川智能 | `Baichuan4` | `baichuan:Baichuan4` |
| `spark` | 讯飞星火 | `4.0Ultra` | `spark:4.0Ultra` |
| `iflytek` | 讯飞星火 x2 新版本 | `spark-v3.5` | `iflytek:spark-v3.5` |
| `stepfun` | 阶跃星辰 | `step-v1` | `stepfun:step-v1` |
| `minimax` | MiniMax | `MiniMax-M2` | `minimax:MiniMax-M2` |
| `longcat` | 美团 Longcat | `LongCat-Flash-Chat` | `longcat:LongCat-Flash-Chat` |
| `siliconflow` | 硅基流动 | `BAAI/bge-m3` | `siliconflow:BAAI/bge-m3` |
| `siliconrouter` | SiliconRouter 路由平台 | — | `siliconrouter:<model>` |
| `dmxapi` | 多模态大模型 API 聚合平台 | `gemini-2.5-flash-nothinking` | `dmxapi:gemini-2.5-flash-nothinking` |
| `mimo` | 小米 MiMo | — | `mimo:<model>` |
| `xiaomi` | 小米 (同mimo) | — | `xiaomi:<model>` |
| `hermes_agent` | Hermes Agent 代理服务 | `deepseek-v4-pro` | `hermes_agent:deepseek-v4-pro` |
| `ollama` | Ollama 本地部署 | `qwen3:30b` | `ollama:qwen3:30b` |
| `yunwu` | 云雾 | `deepseek-chat` | `yunwu:deepseek-chat` |
| `custom` | 自定义 OpenAI 兼容接口 | 用户自定义 | `custom:<model>` |

> **说明**：`dashscope` 与 `qwen` 使用相同的 API 端点；`xiaomi` 与 `mimo` 使用相同的 API 端点。`custom` 提供商需要设置 `CUSTOM_BASE_URL` 和 `CUSTOM_API_KEY` 环境变量。

## 安装

你可以只安装基础的 `aisuite4cn` 包，这只会安装基础包，而不会安装任何提供商的SDK。
或者同时安装某个提供商的包和 `aisuite4cn`包。

请注意，在 create() 调用中的模型名称使用格式为 `<provider>:<model-name>`。 
`aisuite4cn` 将根据提供商值调用相应的提供商并传递正确的参数。 
提供商的列表可以在目录 `aisuite4cn/providers/` 中找到。
支持的提供商的格式为该目录下的 `<provider>_provider.py`。

```shell
pip install aisuite4cn
```

安装通义千问大模型供应商的包

```shell
pip install 'aisuite4cn[qwen]'
```

安装所有大模型供应商的包

```shell
pip install 'aisuite4cn[all]'
```

## 配置

你需要为你打算使用的提供商获取 API 密钥。API 密钥有两种配置方式：

### 方式一：环境变量

设置环境变量后，客户端会自动读取。你可以使用工具如 `python-dotenv` 或 `direnv` 来手动设置环境变量。

```shell
# Moonshot（月之暗面）
export MOONSHOT_API_KEY="your-moonshot-api-key"

# Qwen / Dashscope（阿里云千问 / 百炼平台）
export DASHSCOPE_API_KEY="your-dashscope-api-key"

# Ark / Doubao（火山引擎方舟）
export ARK_API_KEY="your-ark-api-key"

# Hunyuan（腾讯混元）
export HUNYUAN_API_KEY="your-hunyuan-api-key"

# ZhipuAI（智谱AI）
export ZHIPUAI_API_KEY="your-zhipuai-api-key"

# Qianfan / Ernie（百度千帆 / 文心一言）
export QIANFAN_ACCESS_KEY="your-qianfan-access-key"
export QIANFAN_SECRET_KEY="your-qianfan-secret-key"

# DeepSeek（深度求索）
export DEEPSEEK_API_KEY="your-deepseek-api-key"

# Baichuan（百川智能）
export BAICHUAN_API_KEY="your-baichuan-api-key"

# Minimax
export MINIMAX_API_KEY="your-minimax-api-key"

# Stepfun（阶跃星辰）
export STEP_API_KEY="your-step-api-key"

# Yunwu（云雾）
export YUNWU_API_KEY="your-yunwu-api-key"

# Spark（讯飞星火，按模型名映射api-key）
export SPARK_API_KEY_MAP="4.0Ultra=your-key&generalv3=your-key"

# iFlytek（讯飞星火 x2 新版本）
export IFLYTEK_API_KEY="your-iflytek-api-key"

# DMXAPI（多模态大模型API聚合平台）
export DMXAPI_API_KEY="your-dmxapi-api-key"

# Longcat（美团Longcat）
export LONGCAT_API_KEY="your-longcat-api-key"

# Siliconflow（硅基流动）
export SILICONFLOW_API_KEY="your-siliconflow-api-key"

# SiliconRouter
export SILICONROUTER_API_KEY="your-siliconrouter-api-key"

# Mimo / Xiaomi（小米MiMo）
export MIMO_API_KEY="your-mimo-api-key"

# Hermes Agent
export HERMES_AGENT_API_KEY="your-hermes-agent-api-key"
export HERMES_AGENT_BASE_URL="your-hermes-agent-base-url"

# Ollama（本地部署）
export OLLAMA_BASE_URL="your-ollama-base-url"

# Custom（自定义OpenAI兼容接口）
export CUSTOM_BASE_URL="your-custom-base-url"
export CUSTOM_API_KEY="your-custom-api-key"
```

### 方式二：通过 `provider_configs` 参数传入

在初始化 `Client` 时，可以通过 `provider_configs` 字典直接传入各提供商的配置，无需设置环境变量。

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

也可以在初始化后通过 `configure()` 方法动态添加或更新配置：

```python
client = ai.Client()
client.configure({
    "qwen": {"api_key": "your-dashscope-api-key"},
})
```

> **说明**：通过 `provider_configs` 传入的配置优先级高于环境变量。配置字典的 key 为提供商名称（如 `qwen`、`moonshot`），value 为该提供商 `__init__` 方法接受的参数字典（通常包含 `api_key`，部分提供商还支持 `base_url`）。

### 使用示例
```python
import aisuite4cn as ai
client = ai.Client()

# 模型名称格式: provider:model-name
response = client.chat.completions.create(
    model="qwen:qwen-max",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ],
    temperature=0.75
)
print(response.choices[0].message.content)

# 多模型对比
models = [
    "deepseek:deepseek-chat",
    "moonshot:moonshot-v1-8k",
    "qwen:qwen-max",
    "zhipuai:glm-4-flash",
    "hunyuan:hunyuan-standard",
    "qianfan:ernie-3.5-8k",
    "spark:4.0Ultra",
    "minimax:MiniMax-Text-01",
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

## License
`aisuite4cn` 在 MIT 许可证下发布。您可以自由地将代码用于商业和非商业目的。


## Integrated Open source project
Special thanks to all contributors

### aisuite
https://github.com/andrewyng/aisuite

### openai-python
https://github.com/openai/openai-python


## Development Guide
Please refer to [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development and installation instructions.
