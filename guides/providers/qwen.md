# Qwen（阿里云千问 / 百炼）

阿里云百炼平台提供通义千问（Qwen）系列大模型，支持 Chat Completions 和 Embeddings API，是 `aisuite4cn` 中功能最完整的提供商之一。

官网：https://bailian.console.aliyun.com/

## 环境变量

```shell
export DASHSCOPE_API_KEY="your-dashscope-api-key"
```

获取方式：登录阿里云百炼控制台 → [API Key 管理](https://bailian.console.aliyun.com/?apiKey=1#/api-key-center) → 生成新密钥。

## 安装

```shell
pip install 'aisuite4cn[qwen]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="qwen:qwen-max",
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
    model="qwen:qwen-max",
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
    model="qwen:qwen-max",
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
        model="qwen:qwen-max",
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
    "qwen": {"api_key": "your-dashscope-api-key"},
})

response = client.chat.completions.create(
    model="qwen:qwen-max",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 推荐模型

| 模型 ID | 说明 |
|---------|------|
| `qwen-max` | 千问旗舰模型，最强能力 |
| `qwen-plus` | 千问 Plus，均衡性能 |
| `qwen-turbo` | 千问 Turbo，高速低成本 |
| `qwen-long` | 千问 Long，超长上下文 |
| `qwen3-235b-a22b` | Qwen3 MoE 旗舰，235B 参数 |
| `qwen3-32b` | Qwen3 32B，性价比之选 |

## 特殊说明

- `qwen` 和 `dashscope` 是同一 API 端点的两个别名，使用任一均可
- Qwen 同时支持 Embeddings API：`client.embeddings.create(model="qwen:text-embedding-v3", input="文本")`
- 百炼平台还提供图像生成、语音等多模态能力（需使用对应专用 SDK）
