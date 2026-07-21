# Qianfan（百度千帆 / 文心一言）

百度千帆大模型平台提供文心一言系列模型，支持 IAM 认证和 API Key 两种认证方式。

官网：https://cloud.baidu.com/product/wenxinworkshop

## 环境变量

**方式一：IAM 认证（推荐）**

```shell
export QIANFAN_ACCESS_KEY="your-qianfan-access-key"
export QIANFAN_SECRET_KEY="your-qianfan-secret-key"
```

**方式二：API Key**

```shell
export QIANFAN_API_KEY="your-qianfan-api-key"
```

获取方式：登录百度智能云控制台 → [安全认证](https://console.bce.baidu.com/iam/#/iam/accesslist) → 获取 Access Key 和 Secret Key。

## 安装

```shell
pip install 'aisuite4cn[qianfan]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="qianfan:ernie-3.5-8k",
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
    model="qianfan:ernie-3.5-8k",
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
    model="qianfan:ernie-3.5-8k",
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
        model="qianfan:ernie-3.5-8k",
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
    "qianfan": {"api_key": "your-qianfan-api-key"},
    # 或使用 IAM 认证：
    # "qianfan": {"access_key": "xxx", "secret_key": "xxx"},
})

response = client.chat.completions.create(
    model="qianfan:ernie-3.5-8k",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 推荐模型

| 模型 ID | 说明 |
|---------|------|
| `ernie-3.5-8k` | ERNIE 3.5，8K 上下文，性价比高 |
| `ernie-4.0-8k` | ERNIE 4.0，8K 上下文，更强能力 |
| `ernie-4.0-turbo-8k` | ERNIE 4.0 Turbo，高速推理 |
| `ernie-speed-128k` | ERNIE Speed，128K 超长上下文 |

## 特殊说明

- 千帆使用百度 V2 API，认证方式不同于标准 OpenAI API Key
- IAM 认证会自动获取并刷新 Bearer Token，无需手动管理
- 支持 `QIANFAN_API_KEY` 直接传入 API Key，跳过 IAM 流程
