# DeepSeek（深度求索）

DeepSeek 是深度求索推出的大语言模型，以高性价比和推理能力著称，支持 Chat Completions 和 Embeddings API。

官网：https://platform.deepseek.com/

## 环境变量

```shell
export DEEPSEEK_API_KEY="your-deepseek-api-key"
```

获取方式：登录 DeepSeek 平台 → [API Keys](https://platform.deepseek.com/api_keys) → 生成新密钥。

## 安装

```shell
pip install 'aisuite4cn[deepseek]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="deepseek:deepseek-chat",
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
    model="deepseek:deepseek-chat",
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
    model="deepseek:deepseek-chat",
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
        model="deepseek:deepseek-chat",
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
    "deepseek": {"api_key": "your-deepseek-api-key"},
})

response = client.chat.completions.create(
    model="deepseek:deepseek-chat",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 推荐模型

| 模型 ID | 说明 |
|---------|------|
| `deepseek-chat` | DeepSeek-V3 通用对话模型 |
| `deepseek-reasoner` | DeepSeek-R1 推理模型，支持 reasoning_content |

## 特殊说明

- `deepseek-reasoner` 模型返回的 `reasoning_content` 字段包含推理链内容，可通过 `response.choices[0].message.reasoning_content` 获取
- DeepSeek 同时支持 Embeddings API：`client.embeddings.create(model="deepseek:text-embedding-v3", input="文本")`
