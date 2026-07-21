# Ollama（本地部署）

Ollama 是本地大模型运行框架，支持在本地部署和运行多种开源模型（如 Llama、Qwen、DeepSeek 等）。

官网：https://ollama.com/

## 环境变量

```shell
export OLLAMA_BASE_URL="http://localhost:11434/v1"
```

## 安装

**1. 安装 Ollama**

参考 [Ollama 官方文档](https://ollama.com/download) 安装 Ollama。

**2. 拉取模型**

```shell
ollama pull qwen3:30b
```

**3. 安装 aisuite4cn**

```shell
pip install 'aisuite4cn[ollama]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="ollama:qwen3:30b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你好！"},
    ],
)
print(response.choices[0].message.content)
```

### Responses API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.responses.create(
    model="ollama:qwen3:30b",
    input="你好！",
    instructions="You are a helpful assistant.",
)
print(response.output[0].content[0].text)
```

### 流式输出

```python
import aisuite4cn as ai

client = ai.Client()

stream = client.chat.completions.create(
    model="ollama:qwen3:30b",
    messages=[
        {"role": "user", "content": "讲一个笑话"},
    ],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### 异步调用

```python
import asyncio
import aisuite4cn as ai

async def main():
    client = ai.AsyncClient()
    response = await client.chat.completions.create(
        model="ollama:qwen3:30b",
        messages=[
            {"role": "user", "content": "你好！"},
        ],
    )
    print(response.choices[0].message.content)

asyncio.run(main())
```

### provider_configs 方式

```python
import aisuite4cn as ai

client = ai.Client(provider_configs={
    "ollama": {"base_url": "http://localhost:11434/v1"},
})

response = client.chat.completions.create(
    model="ollama:qwen3:30b",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 推荐模型

| 模型 ID | 说明 |
|---------|------|
| `qwen3:30b` | Qwen3 30B，支持推理 |
| `deepseek-r1:7b` | DeepSeek-R1 7B，推理模型 |
| `llama3.1:8b` | Llama 3.1 8B |
| `gemma2:9b` | Gemma 2 9B |

## 特殊说明

- `OLLAMA_BASE_URL` 必须设置，通常为 `http://localhost:11434/v1`
- Ollama 的推理模型（如 deepseek-r1、qwen3）使用 `<think>...</think>` 标签包裹思考内容，`aisuite4cn` 会自动将其转换为标准的 `reasoning_content` 字段
- 流式和非流式模式均支持 think tag 自动转换
- `api_key` 在未设置时默认使用 `"ollama"` 占位值
