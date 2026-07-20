# aisuite4cn Gateway

`aisuite4cn Gateway` 是一个 HTTP API 网关，为 aisuite4cn 提供统一的 RESTful 接口。通过 Gateway，你可以将 aisuite4cn 的 LLM 调用能力暴露为标准 OpenAI 兼容的 HTTP 服务，支持 **Chat Completions API** 和 **Responses API** 双协议。

## 安装

```shell
# 安装 gateway 依赖（fastapi + uvicorn + click + pyyaml）
pip install 'aisuite4cn[gateway]'

# 或使用 uv
uv sync --extra gateway
```

## 快速开始

### 1. 配置 Provider

创建配置文件 `~/.aisuite4cn/config.yaml`（自动加载），或通过 `--config` 指定：

```yaml
# ~/.aisuite4cn/config.yaml
providers:
  deepseek:
    api_key: "sk-your-deepseek-api-key"
  qwen:
    api_key: "sk-your-dashscope-api-key"
```

### 2. 启动 Gateway

```shell
# 使用默认配置文件 (~/.aisuite4cn/config.yaml) 启动
aisuite4cn gateway start

# 指定配置文件
aisuite4cn gateway start --config /path/to/config.yaml

# 指定端口
aisuite4cn gateway start --port 8080
```

### 3. 调用 API

```shell
# 健康检查
curl http://localhost:8000/health

# Chat Completions
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek:deepseek-chat",
    "messages": [{"role": "user", "content": "你好！"}]
  }'

# Responses API
curl -X POST http://localhost:8000/v1/responses \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek:deepseek-chat",
    "input": "你好！"
  }'

# 流式输出
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek:deepseek-chat",
    "messages": [{"role": "user", "content": "讲个笑话"}],
    "stream": true
  }'
```

## CLI 命令

### aisuite4cn gateway start

启动 Gateway 服务器（后台运行）。

```shell
aisuite4cn gateway start [OPTIONS]
```

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--host TEXT` | 绑定地址 | `0.0.0.0` |
| `--port INTEGER` | 绑定端口 | `8000` |
| `-c, --config TEXT` | 配置文件路径 | `~/.aisuite4cn/config.yaml` |
| `--reload` | 自动重载（仅开发用） | `false` |

### aisuite4cn gateway stop

停止后台运行的 Gateway 服务器。

```shell
aisuite4cn gateway stop
```

### aisuite4cn gateway restart

重启 Gateway 服务器。

```shell
aisuite4cn gateway restart [OPTIONS]
```

选项同 `start`。

## API 端点

### GET /health

健康检查。

```json
{
  "status": "healthy",
  "service": "aisuite4cn-gateway"
}
```

### GET /v1/models

列出所有可用的 Provider。

```json
{
  "object": "list",
  "data": [
    {"id": "ark:default", "object": "model", "owned_by": "ark"},
    {"id": "deepseek:default", "object": "model", "owned_by": "deepseek"},
    ...
  ]
}
```

### POST /v1/chat/completions

Chat Completions API，完全兼容 OpenAI 格式。

**请求参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `model` | string | 模型标识，格式 `provider:model-name` |
| `messages` | array | 消息列表 |
| `temperature` | float | 温度参数 |
| `top_p` | float | top_p 采样 |
| `max_tokens` | int | 最大输出 token 数 |
| `stream` | bool | 是否流式输出 |
| `tools` | array | 工具定义 |
| `tool_choice` | string/object | 工具选择策略 |
| 其他 | — | 透传给对应 Provider |

**响应示例：**

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "deepseek:deepseek-chat",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "你好！有什么可以帮你的吗？"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

### POST /v1/responses

Responses API，兼容 OpenAI Responses 协议。

**请求参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `model` | string | 模型标识，格式 `provider:model-name` |
| `input` | string/array | 输入内容 |
| `instructions` | string | 系统指令 |
| `max_output_tokens` | int | 最大输出 token 数 |
| `stream` | bool | 是否流式输出 |
| `tools` | array | 工具定义 |
| 其他 | — | 透传给对应 Provider |

**响应示例：**

```json
{
  "id": "resp_xxx",
  "object": "response",
  "created": 1700000000,
  "model": "deepseek:deepseek-chat",
  "output": [
    {
      "type": "message",
      "role": "assistant",
      "content": [
        {"type": "output_text", "text": "你好！"}
      ]
    }
  ],
  "usage": {
    "input_tokens": 10,
    "output_tokens": 20,
    "total_tokens": 30
  }
}
```

## 配置文件

### 加载优先级

1. `--config` / `-c` 显式指定的配置文件（最高优先级）
2. `~/.aisuite4cn/config.yaml`（默认位置，如果存在）
3. 空配置

### 配置格式（YAML）

```yaml
providers:
  deepseek:
    api_key: "sk-your-deepseek-api-key"

  qwen:
    api_key: "sk-your-dashscope-api-key"

  openai_compatible_custom:
    base_url: "https://your-provider.com/v1"
    api_key: "your-api-key"
```

### JSON 格式也支持

```json
{
  "providers": {
    "deepseek": {
      "api_key": "sk-your-deepseek-api-key"
    }
  }
}
```

### 各 Provider 配置参考

| Provider | 配置项 | 说明 |
|----------|--------|------|
| `deepseek` | `api_key` | DeepSeek API Key |
| `qwen` / `dashscope` | `api_key` | 通义千问 API Key |
| `ark` | `api_key` | 火山引擎 API Key |
| `moonshot` | `api_key` | Kimi API Key |
| `zhipuai` | `api_key` | 智谱 GLM API Key |
| `baichuan` | `api_key` | 百川 API Key |
| `hunyuan` | `api_key` | 腾讯混元 API Key |
| `minimax` | `api_key`, `base_url?` | MiniMax（base_url 可选） |
| `stepfun` | `api_key` | 阶跃星辰 API Key |
| `longcat` | `api_key` | LongCat API Key |
| `siliconflow` | `api_key` | 硅基流动 API Key |
| `siliconrouter` | `api_key` | 硅基路由 API Key |
| `dmxapi` | `api_key`, `base_url?` | DMXAPI（base_url 可选） |
| `yunwu` | `api_key` | 云雾 API Key |
| `iflytek` | `api_key` | 讯飞星火 x2 API Key |
| `spark` | `api_key_map` | 讯飞星火新版，按模型映射密码 |
| `mimo` / `xiaomi` | `api_key`, `base_url?` | 小米 MiMo（base_url 可选） |
| `qianfan` | `api_key` 或 `access_key` + `secret_key` | 百度千帆（两种认证方式） |
| `ollama` | `base_url`, `api_key?` | 本地部署（仅需 base_url） |
| `custom` | `base_url`, `api_key?` | 自定义兼容接口 |
| `openclaw` | `base_url`, `api_key?` | 自部署网关 |
| `hermes_agent` | `base_url`, `api_key?` | 服务端 Agent |

> 完整示例配置见 `aisuite4cn/gateway/config.example.yaml`。

## Docker 部署

### 构建镜像

```shell
docker build -f aisuite4cn/gateway/Dockerfile -t aisuite4cn-gateway .
```

### 使用环境变量

```shell
docker run -d \
  --name aisuite4cn-gateway \
  -p 8000:8000 \
  -e DEEPSEEK_API_KEY=sk-xxx \
  -e DASHSCOPE_API_KEY=sk-yyy \
  aisuite4cn-gateway
```

### 使用配置文件

```shell
# 准备配置文件
mkdir -p ~/.aisuite4cn
cat > ~/.aisuite4cn/config.yaml << 'EOF'
providers:
  deepseek:
    api_key: "sk-your-deepseek-api-key"
  qwen:
    api_key: "sk-your-dashscope-api-key"
EOF

# 挂载配置文件
docker run -d \
  --name aisuite4cn-gateway \
  -p 8000:8000 \
  -v ~/.aisuite4cn/config.yaml:/home/gateway/.aisuite4cn/config.yaml \
  aisuite4cn-gateway
```

### 使用自定义配置路径

```shell
docker run -d \
  --name aisuite4cn-gateway \
  -p 8000:8000 \
  -v /path/to/my-config.yaml:/app/config.yaml \
  -e AISUITE_GATEWAY_CONFIG=/app/config.yaml \
  aisuite4cn-gateway
```

### Docker Compose

```yaml
version: "3.8"

services:
  gateway:
    build:
      context: .
      dockerfile: aisuite4cn/gateway/Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./config.yaml:/home/gateway/.aisuite4cn/config.yaml
    restart: unless-stopped
```

## 进程管理

Gateway 使用 PID 文件进行进程管理，默认位置 `~/.aisuite4cn/gateway.pid`。

```shell
# 查看日志
tail -f ~/.aisuite4cn/gateway.log

# 检查状态
aisuce4cn gateway stop  # 如果未运行会提示

# 强制清理（异常退出后）
rm ~/.aisuite4cn/gateway.pid
```

## SDK 调用示例

Gateway 暴露标准 OpenAI 兼容接口，可以直接使用 OpenAI SDK：

### Python (openai SDK)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed",  # Gateway 内部已配置 Provider Key
)

# Chat Completions
response = client.chat.completions.create(
    model="deepseek:deepseek-chat",
    messages=[{"role": "user", "content": "你好"}],
)
print(response.choices[0].message.content)

# 流式
for chunk in client.chat.completions.create(
    model="deepseek:deepseek-chat",
    messages=[{"role": "user", "content": "你好"}],
    stream=True,
):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### JavaScript (@openai/openai)

```javascript
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "http://localhost:8000/v1",
  apiKey: "not-needed",
});

const response = await client.chat.completions.create({
  model: "deepseek:deepseek-chat",
  messages: [{ role: "user", content: "你好" }],
});
console.log(response.choices[0].message.content);
```

### cURL

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek:deepseek-chat","messages":[{"role":"user","content":""}]}'
```
