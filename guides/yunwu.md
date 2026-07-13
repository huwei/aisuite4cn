# Yunwu（云雾）

云雾 AI 是一个多模型聚合平台，提供 DeepSeek 等多种模型的 API 访问。

官网：https://yunwu.ai/

## 环境变量

```shell
export YUNWU_API_KEY="your-yunwu-api-key"
```

获取方式：登录云雾 AI 平台 → 获取 API Key。

## 安装

```shell
pip install 'aisuite4cn[yunwu]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="yunwu:deepseek-chat",
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
    model="yunwu:deepseek-chat",
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
    model="yunwu:deepseek-chat",
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
        model="yunwu:deepseek-chat",
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
    "yunwu": {"api_key": "your-yunwu-api-key"},
})

response = client.chat.completions.create(
    model="yunwu:deepseek-chat",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 推荐模型

| 模型 ID | 说明 |
|---------|------|
| `deepseek-chat` | DeepSeek V3 通用对话 |
| `deepseek-reasoner` | DeepSeek R1 推理模型 |

## 特殊说明

- 云雾是聚合平台，具体可用模型以平台为准
- 模型名称参考平台文档，与原厂模型名称一致
