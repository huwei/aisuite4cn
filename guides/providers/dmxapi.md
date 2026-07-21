# DMXAPI（多模态 API 聚合平台）

DMXAPI 是一个多模型聚合平台，通过统一接口访问多种第三方大模型（如 Gemini、Claude 等）。

官网：https://www.dmxapi.cn/

## 环境变量

```shell
export DMXAPI_API_KEY="your-dmxapi-api-key"
```

获取方式：登录 DMXAPI 平台 → 获取 API Key。

## 安装

```shell
pip install 'aisuite4cn[dmxapi]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="dmxapi:gemini-2.5-flash",
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
    model="dmxapi:gemini-2.5-flash",
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
    model="dmxapi:gemini-2.5-flash",
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
        model="dmxapi:gemini-2.5-flash",
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
    "dmxapi": {"api_key": "your-dmxapi-api-key"},
})

response = client.chat.completions.create(
    model="dmxapi:gemini-2.5-flash",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 推荐模型

| 模型 ID | 说明 |
|---------|------|
| `gemini-2.5-flash` | Google Gemini 2.5 Flash |
| `gemini-2.5-pro` | Google Gemini 2.5 Pro |
| `claude-sonnet-4-20250514` | Anthropic Claude Sonnet 4 |

## 特殊说明

- DMXAPI 是聚合平台，模型名称需参考平台提供的模型列表
- 默认 base_url 为 `https://www.dmxapi.cn/v1`，可通过 `DMXAPI_BASE_URL` 环境变量或 config 覆盖
- 具体可用模型和价格以 DMXAPI 平台为准
