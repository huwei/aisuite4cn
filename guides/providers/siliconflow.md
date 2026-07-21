# SiliconFlow（硅基流动）

硅基流动是一个多模型聚合平台，通过统一接口访问多种开源大模型。

官网：https://siliconflow.cn/

## 环境变量

```shell
export SILICONFLOW_API_KEY="your-siliconflow-api-key"
```

获取方式：登录硅基流动平台 → 获取 API Key。

## 安装

```shell
pip install 'aisuite4cn[siliconflow]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="siliconflow:Qwen/Qwen3-8B",
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
    model="siliconflow:Qwen/Qwen3-8B",
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
    model="siliconflow:Qwen/Qwen3-8B",
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
        model="siliconflow:Qwen/Qwen3-8B",
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
    "siliconflow": {"api_key": "your-siliconflow-api-key"},
})

response = client.chat.completions.create(
    model="siliconflow:Qwen/Qwen3-8B",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 推荐模型

| 模型 ID | 说明 |
|---------|------|
| `Qwen/Qwen3-8B` | Qwen3 8B |
| `deepseek-ai/DeepSeek-R1` | DeepSeek R1 推理模型 |
| `BAAI/bge-m3` | Embeddings 模型 |

## 特殊说明

- SiliconFlow 同时支持 Embeddings API：`client.embeddings.create(model="siliconflow:BAAI/bge-m3", input="文本")`
- 模型名称格式参考平台提供的模型列表
