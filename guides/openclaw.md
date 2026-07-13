# OpenClaw（OpenClaw 网关）

OpenClaw 是一个网关服务，对外提供 OpenAI 兼容的 HTTP API，底层作为 Gateway 网关智能体运行。

官网：https://docs.openclaw.ai/

## 环境变量

```shell
export OPENCLAW_BASE_URL="your-openclaw-base-url"
export OPENCLAW_API_KEY="your-openclaw-api-key"  # 可选，none 认证模式可省略
```

认证方式取决于网关配置：
- `gateway.auth.mode="token"` 或 `"password"`：需提供 `OPENCLAW_API_KEY`（或 `OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`）
- `gateway.auth.mode="none"`：无需认证，`api_key` 可使用任意占位值

## 安装

```shell
pip install 'aisuite4cn[openclaw]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="openclaw:your-model-name",
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
    model="openclaw:your-model-name",
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
    model="openclaw:your-model-name",
    messages=[
        {"role": "user", "content": "讲一个笑话"},
    ],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### provider_configs 方式

```python
import aisuite4cn as ai

client = ai.Client(provider_configs={
    "openclaw": {
        "base_url": "http://your-openclaw-gateway:port/v1",
        "api_key": "your-api-key",
    },
})

response = client.chat.completions.create(
    model="openclaw:your-model-name",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 特殊说明

- `OPENCLAW_BASE_URL` 必须设置，指向 OpenClaw 网关地址
- 认证模式由网关配置决定，常见为共享密钥模式（`gateway.auth.mode="token"`）
- 参考：[OpenClaw Gateway OpenAI HTTP API 文档](https://docs.openclaw.ai/zh-CN/gateway/openai-http-api)
