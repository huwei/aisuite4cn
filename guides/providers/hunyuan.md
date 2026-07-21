# Hunyuan（腾讯云混元大模型）

腾讯混元是腾讯云推出的大语言模型服务，提供标准版、Turbo 等多种规格。

官网：https://cloud.tencent.com/product/hunyuan

## 环境变量

```shell
export HUNYUAN_API_KEY="your-hunyuan-api-key"
```

获取方式：
1. 登录 [腾讯云控制台](https://console.cloud.tencent.com/) → [开通服务](https://console.cloud.tencent.com/hunyuan/settings) → 激活混元服务
2. 进入 [API Keys](https://console.cloud.tencent.com/hunyuan/api-key) → 生成新密钥

## 安装

```shell
pip install 'aisuite4cn[hunyuan]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="hunyuan:hunyuan-standard",
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
    model="hunyuan:hunyuan-standard",
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
    model="hunyuan:hunyuan-standard",
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
        model="hunyuan:hunyuan-standard",
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
    "hunyuan": {"api_key": "your-hunyuan-api-key"},
})

response = client.chat.completions.create(
    model="hunyuan:hunyuan-standard",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 推荐模型

| 模型 ID | 说明 |
|---------|------|
| `hunyuan-standard` | 混元标准版，均衡性能 |
| `hunyuan-turbo-latest` | 混元 Turbo 最新版，高性能 |
| `hunyuan-large-latest` | 混元 Large，最强能力 |
