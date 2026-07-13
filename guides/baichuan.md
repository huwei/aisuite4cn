# Baichuan（百川智能）

百川智能推出的大语言模型服务，提供 Baichuan 系列模型。

官网：https://platform.baichuan-ai.com/

## 环境变量

```shell
export BAICHUAN_API_KEY="your-baichuan-api-key"
```

获取方式：登录百川智能开放平台 → [API Keys](https://platform.baichuan-ai.com/console/apikey) → 生成新密钥。

## 安装

```shell
pip install 'aisuite4cn[baichuan]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="baichuan:Baichuan4",
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
    model="baichuan:Baichuan4",
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
    model="baichuan:Baichuan4",
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
        model="baichuan:Baichuan4",
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
    "baichuan": {"api_key": "your-baichuan-api-key"},
})

response = client.chat.completions.create(
    model="baichuan:Baichuan4",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 推荐模型

| 模型 ID | 说明 |
|---------|------|
| `Baichuan4` | 百川 4，最新旗舰模型 |
| `Baichuan3-turbo` | 百川 3 Turbo，高速推理 |
| `Baichuan3-turbo-128k` | 百川 3 Turbo，128K 上下文 |
