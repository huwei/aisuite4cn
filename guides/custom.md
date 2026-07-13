# Custom（自定义 OpenAI 兼容接口）

自定义 Provider，用于对接任意 OpenAI 兼容的 API 端点。只需提供 `base_url` 和 `api_key` 即可使用。

## 环境变量

```shell
export CUSTOM_BASE_URL="your-custom-base-url"
export CUSTOM_API_KEY="your-custom-api-key"
```

## 安装

```shell
pip install 'aisuite4cn[custom]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="custom:your-model-name",
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
    model="custom:your-model-name",
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
    model="custom:your-model-name",
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
        model="custom:your-model-name",
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
    "custom": {
        "base_url": "https://your-api-endpoint.com/v1",
        "api_key": "your-api-key",
    },
})

response = client.chat.completions.create(
    model="custom:your-model-name",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 特殊说明

- `custom` provider 需要同时设置 `CUSTOM_BASE_URL` 和 `CUSTOM_API_KEY`
- 适用于自建服务、内网部署或其他未内置的 OpenAI 兼容 API
- `api_key` 在未设置时默认使用 `"custom"` 占位值（适合无需认证的本地服务）
- 如果已有专用 provider（如 `ollama`、`openclaw`），优先使用专用 provider
