# iFlytek（讯飞星火 x2）

科大讯飞星火 x2 版本 API，使用独立的 API 端点。与 `spark` provider 使用不同的接口地址。

官网：https://xinghuo.xfyun.cn/

## 环境变量

```shell
export IFLYTEK_API_KEY="your-iflytek-api-key"
```

获取方式：登录 [讯飞开放平台](https://console.xfyun.cn/app/myapp) → 创建应用 → 获取 API Key。

## 安装

```shell
pip install 'aisuite4cn[iflytek]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="iflytek:spark-v3.5",
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
    model="iflytek:spark-v3.5",
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
    model="iflytek:spark-v3.5",
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
        model="iflytek:spark-v3.5",
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
    "iflytek": {"api_key": "your-iflytek-api-key"},
})

response = client.chat.completions.create(
    model="iflytek:spark-v3.5",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 推荐模型

| 模型 ID | 说明 |
|---------|------|
| `spark-v3.5` | 星火 3.5 |
| `spark-v3.0` | 星火 3.0 |

## 特殊说明

- iFlytek 不支持 `frequency_penalty` 和 `presence_penalty` 参数，代码会自动过滤
- `iflytek` 和 `spark` 是两个不同的 provider，使用不同的 API 端点和认证方式
