# Moonshot AI（月之暗面）

Moonshot AI 是月之暗面推出的大语言模型服务，以 Kimi 系列模型闻名，支持超长上下文。

官网：https://platform.moonshot.cn/

## 环境变量

```shell
export MOONSHOT_API_KEY="your-moonshot-api-key"
```

获取方式：登录 Moonshot 平台 → [API Keys](https://platform.moonshot.cn/console/api-keys) → 生成新密钥。

## 安装

```shell
pip install 'aisuite4cn[moonshot]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="moonshot:moonshot-v1-8k",
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
    model="moonshot:moonshot-v1-8k",
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
    model="moonshot:moonshot-v1-8k",
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
        model="moonshot:moonshot-v1-8k",
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
    "moonshot": {"api_key": "your-moonshot-api-key"},
})

response = client.chat.completions.create(
    model="moonshot:moonshot-v1-8k",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 推荐模型

| 模型 ID | 说明 |
|---------|------|
| `moonshot-v1-8k` | 8K 上下文，速度快 |
| `moonshot-v1-32k` | 32K 上下文，平衡型 |
| `moonshot-v1-128k` | 128K 上下文，超长文本 |
