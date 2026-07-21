# Ark（火山引擎方舟大模型服务平台）

火山引擎方舟是字节跳动旗下的大模型服务平台，提供豆包（Doubao）等系列模型。

官网：https://console.volcengine.com/ark

## 环境变量

```shell
export ARK_API_KEY="your-ark-api-key"
```

获取方式：登录火山引擎控制台 → [API Keys](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey) → 生成新密钥。

## 安装

```shell
pip install 'aisuite4cn[ark]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="ark:doubao-seed-1.6-250615",
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
    model="ark:doubao-seed-1.6-250615",
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
    model="ark:doubao-seed-1.6-250615",
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
        model="ark:doubao-seed-1.6-250615",
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
    "ark": {"api_key": "your-ark-api-key"},
})

response = client.chat.completions.create(
    model="ark:doubao-seed-1.6-250615",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 推荐模型

| 模型 ID | 说明 |
|---------|------|
| `doubao-seed-1.6-250615` | 豆包最新旗舰模型 |
| `doubao-1.5-pro-256k` | 豆包 1.5 Pro，支持 256K 上下文 |
| `doubao-1.5-lite-32k` | 豆包 1.5 Lite，轻量高速 |

## 特殊说明

- 模型 ID 需在火山引擎控制台 [推理接入点](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint) 中创建获取
- Ark 的模型 ID 是 endpoint ID，不是模型名称
