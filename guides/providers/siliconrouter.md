# SiliconRouter

SiliconRouter 是一个 API 路由服务。

官网：https://www.siliconrouter.com/

## 环境变量

```shell
export SILICONROUTER_API_KEY="your-siliconrouter-api-key"
```

获取方式：登录 SiliconRouter 平台 → 获取 API Key。

## 安装

```shell
pip install 'aisuite4cn[siliconrouter]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="siliconrouter:your-model-name",
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
    model="siliconrouter:your-model-name",
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
    model="siliconrouter:your-model-name",
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
        model="siliconrouter:your-model-name",
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
    "siliconrouter": {"api_key": "your-siliconrouter-api-key"},
})

response = client.chat.completions.create(
    model="siliconrouter:your-model-name",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 特殊说明

- 默认 base_url 为 `https://api.siliconrouter.com/v1`，可通过 config 覆盖
- 具体可用模型以 SiliconRouter 平台为准
