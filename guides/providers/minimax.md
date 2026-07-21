# MiniMax

MiniMax 大语言模型服务，提供 MiniMax-M2 等模型。

官网：https://www.minimaxi.com/

## 环境变量

```shell
export MINIMAX_API_KEY="your-minimax-api-key"
```

获取方式：登录 MiniMax 平台 → 获取 API Key。

## 安装

```shell
pip install 'aisuite4cn[minimax]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="minimax:MiniMax-M2",
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
    model="minimax:MiniMax-M2",
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
    model="minimax:MiniMax-M2",
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
        model="minimax:MiniMax-M2",
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
    "minimax": {"api_key": "your-minimax-api-key"},
})

response = client.chat.completions.create(
    model="minimax:MiniMax-M2",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 推荐模型

| 模型 ID | 说明 |
|---------|------|
| `MiniMax-M2` | MiniMax M2，通用对话模型 |

## 特殊说明

- 默认 base_url 为 `https://api.minimaxi.com/v1`，可通过 `MINIMAX_BASE_URL` 环境变量覆盖
