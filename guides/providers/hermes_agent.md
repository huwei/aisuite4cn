# Hermes Agent（代理服务）

Hermes Agent 是一个服务端自主执行工具的 AI 代理服务，暴露 OpenAI 兼容端点。工具在服务端执行，客户端无需回传工具结果。

## 环境变量

```shell
export HERMES_AGENT_BASE_URL="your-hermes-agent-base-url"
export HERMES_AGENT_API_KEY="your-hermes-agent-api-key"  # 可选，内网部署可留空
```

## 安装

```shell
pip install 'aisuite4cn[hermes_agent]'
```

## 使用示例

### Chat Completions API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.chat.completions.create(
    model="hermes_agent:deepseek-v4-pro",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "帮我查看当前目录的文件"},
    ],
)
print(response.choices[0].message.content)
```

### Responses API

```python
import aisuite4cn as ai

client = ai.Client()

response = client.responses.create(
    model="hermes_agent:deepseek-v4-pro",
    input="帮我查看当前目录的文件",
    instructions="You are a helpful assistant.",
)
print(response.output[0].content[0].text)
```

### 流式输出

```python
import aisuite4cn as ai

client = ai.Client()

stream = client.chat.completions.create(
    model="hermes_agent:deepseek-v4-pro",
    messages=[
        {"role": "user", "content": "帮我查看当前目录的文件"},
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
    "hermes_agent": {
        "base_url": "http://your-hermes-agent:18642/v1",
        "api_key": "your-api-key",
    },
})

response = client.chat.completions.create(
    model="hermes_agent:deepseek-v4-pro",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## 特殊说明

- `HERMES_AGENT_BASE_URL` 必须设置，指向 Hermes Agent 服务地址（如 `http://localhost:18642/v1`）
- 工具在服务端自主执行，客户端无需处理工具调用结果
- 流式输出中会自动将 `hermes.tool.progress` SSE 事件转换为 OpenAI 标准 tool_calls 格式
- 转换后的 tool_calls 仅供客户端感知工具执行进度，不需要客户端执行这些工具
