# Stepfun（阶跃星辰）

阶跃星辰推出的大语言模型服务，提供 Step 系列模型。

官网：https://www.stepfun.com/

## 环境变量

```shell
export STEP_API_KEY="your-step-api-key"
```

获取方式：登录阶跃星辰开放平台 → 获取 API Key。

## 安装

```shell
pip install 'aisuite4cn[stepfun]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="stepfun:step-v1",
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
    model="stepfun:step-v1",
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
    model="stepfun:step-v1",
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
        model="stepfun:step-v1",
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
    "stepfun": {"api_key": "your-step-api-key"},
})

response = client.chat.completions.create(
    model="stepfun:step-v1",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 推荐模型

| 模型 ID | 说明 |
|---------|------|
| `step-v1` | Step V1 通用对话模型 |
| `step-2-16k` | Step 2，16K 上下文 |

## 特殊说明

- 默认 base_url 为 `https://api.stepfun.com/v1`，可通过 `STEP_BASE_URL` 环境变量覆盖
