# Mimo（小米 MiMo）

小米 MiMo 大语言模型服务。

官网：https://api.xiaomimimo.com/

## 环境变量

```shell
export MIMO_API_KEY="your-mimo-api-key"
```

获取方式：登录小米 MiMo 平台 → 获取 API Key。

## 安装

```shell
pip install 'aisuite4cn[mimo]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="mimo:your-model-name",
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
    model="mimo:your-model-name",
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
    model="mimo:your-model-name",
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
        model="mimo:your-model-name",
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
    "mimo": {"api_key": "your-mimo-api-key"},
})

response = client.chat.completions.create(
    model="mimo:your-model-name",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 特殊说明

- `mimo` 和 `xiaomi` 是完全等价的别名，使用任一均可
- 默认 base_url 为 `https://api.xiaomimimo.com/v1`，可通过 `MIMO_BASE_URL` 环境变量覆盖
