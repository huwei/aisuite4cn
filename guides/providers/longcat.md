# LongCat（美团 LongCat）

美团 LongCat 大语言模型服务。

官网：https://longcat.chat/

## 环境变量

```shell
export LONGCAT_API_KEY="your-longcat-api-key"
```

获取方式：登录 LongCat 平台 → 获取 API Key。

## 安装

```shell
pip install 'aisuite4cn[longcat]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="longcat:LongCat-Flash-Chat",
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
    model="longcat:LongCat-Flash-Chat",
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
    model="longcat:LongCat-Flash-Chat",
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
        model="longcat:LongCat-Flash-Chat",
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
    "longcat": {"api_key": "your-longcat-api-key"},
})

response = client.chat.completions.create(
    model="longcat:LongCat-Flash-Chat",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 推荐模型

| 模型 ID | 说明 |
|---------|------|
| `LongCat-Flash-Chat` | LongCat Flash Chat，高速对话 |
