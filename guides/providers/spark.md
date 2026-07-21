# Spark（讯飞星火）

科大讯飞星火大模型，使用模型到密钥的映射机制，每个模型对应独立的 API 密钥。

官网：https://xinghuo.xfyun.cn/

## 环境变量

```shell
export SPARK_API_KEY_MAP="4.0Ultra=your-api-password&generalv3=your-api-password"
```

格式：`模型名=API密码&模型名=API密码`，多个模型用 `&` 分隔。

获取方式：
1. 登录 [讯飞开放平台](https://console.xfyun.cn/app/myapp) → 创建应用
2. 进入 [API 中心](https://console.xfyun.cn/services/sparkapiCenter) → 获取各模型的 API 密钥

## 安装

```shell
pip install 'aisuite4cn[spark]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="spark:4.0Ultra",
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
    model="spark:4.0Ultra",
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
    model="spark:4.0Ultra",
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
        model="spark:4.0Ultra",
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
    "spark": {
        "api_key_map": {
            "4.0Ultra": "your-4.0Ultra-api-password",
            "generalv3": "your-generalv3-api-password",
        }
    },
})

response = client.chat.completions.create(
    model="spark:4.0Ultra",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 推荐模型

| 模型 ID | 说明 |
|---------|------|
| `4.0Ultra` | 星火 4.0 Ultra，最强能力 |
| `generalv3.5` | 星火 3.5，通用对话 |
| `generalv3` | 星火 3.0，基础版本 |
| `4.0UltraChat` | 星火 4.0 Ultra Chat 版 |

## 特殊说明

- Spark 的认证方式特殊：每个模型有独立的 API 密钥，通过 `SPARK_API_KEY_MAP` 映射
- 环境变量格式为 `模型名=密钥&模型名=密钥`，URL 编码的 query string 格式
- 也可通过 `provider_configs` 的 `api_key_map` 字典直接传入
- `spark` 和 `iflytek` 是两个不同的 provider，对应讯飞不同的 API 端点
