# ZhipuAI（智谱 AI / GLM）

智谱 AI 推出的 GLM 系列大模型，支持 Chat Completions API。

官网：https://open.bigmodel.cn/

## 环境变量

```shell
export ZHIPUAI_API_KEY="your-zhipuai-api-key"
```

获取方式：登录智谱 AI 开放平台 → [API Keys](https://open.bigmodel.cn/usercenter/proj-mgmt/apikeys) → 生成新密钥。

## 安装

```shell
pip install 'aisuite4cn[zhipuai]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="zhipuai:glm-4-flash",
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
    model="zhipuai:glm-4-flash",
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
    model="zhipuai:glm-4-flash",
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
        model="zhipuai:glm-4-flash",
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
    "zhipuai": {"api_key": "your-zhipuai-api-key"},
})

response = client.chat.completions.create(
    model="zhipuai:glm-4-flash",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 推荐模型

| 模型 ID | 说明 |
|---------|------|
| `glm-4-flash` | GLM-4 Flash，免费高速 |
| `glm-4-plus` | GLM-4 Plus，增强能力 |
| `glm-4-long` | GLM-4 Long，超长上下文 |
| `glm-4-air` | GLM-4 Air，轻量版 |

## 特殊说明

- ZhipuAI 不支持 `frequency_penalty` 和 `presence_penalty` 参数，代码会自动过滤
- `zhipuai` 是标准 pip 包名，但 `aisuite4cn` 内部使用 OpenAI SDK 调用，无需单独安装 `zhipuai` 包
