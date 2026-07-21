# aisuite4cn Provider 指南

本目录包含每个 Provider 的使用指南。`aisuite4cn` 支持 25 个中国大模型提供商，通过统一的 `<provider>:<model-name>` 格式调用。

## 快速开始

```python
import aisuite4cn as ai

client = ai.Client()
response = client.chat.completions.create(
    model="qwen:qwen-max",
    messages=[{"role": "user", "content": "你好！"}],
)
print(response.choices[0].message.content)
```

## Provider 列表

| Provider | 中文名称 | 环境变量 | 示例模型 | 指南 |
|----------|----------|----------|----------|------|
| `qwen` | 阿里云千问 | `DASHSCOPE_API_KEY` | `qwen-max` | [指南](providers/qwen.md) |
| `dashscope` | 阿里云百炼 | `DASHSCOPE_API_KEY` | `qwen-max` | [指南](providers/dashscope.md) |
| `deepseek` | 深度求索 | `DEEPSEEK_API_KEY` | `deepseek-chat` | [指南](providers/deepseek.md) |
| `ark` | 火山引擎方舟 | `ARK_API_KEY` | `doubao-seed-1.6-250615` | [指南](providers/ark.md) |
| `moonshot` | 月之暗面 | `MOONSHOT_API_KEY` | `moonshot-v1-8k` | [指南](providers/moonshot.md) |
| `zhipuai` | 智谱 AI | `ZHIPUAI_API_KEY` | `glm-4-flash` | [指南](providers/zhipuai.md) |
| `hunyuan` | 腾讯混元 | `HUNYUAN_API_KEY` | `hunyuan-standard` | [指南](providers/hunyuan.md) |
| `qianfan` | 百度千帆 | `QIANFAN_ACCESS_KEY` + `QIANFAN_SECRET_KEY` | `ernie-3.5-8k` | [指南](providers/qianfan.md) |
| `spark` | 讯飞星火 | `SPARK_API_KEY_MAP` | `4.0Ultra` | [指南](providers/spark.md) |
| `iflytek` | 讯飞星火 x2 | `IFLYTEK_API_KEY` | `spark-v3.5` | [指南](providers/iflytek.md) |
| `baichuan` | 百川智能 | `BAICHUAN_API_KEY` | `Baichuan4` | [指南](providers/baichuan.md) |
| `minimax` | MiniMax | `MINIMAX_API_KEY` | `MiniMax-M2` | [指南](providers/minimax.md) |
| `stepfun` | 阶跃星辰 | `STEP_API_KEY` | `step-v1` | [指南](providers/stepfun.md) |
| `mimo` | 小米 MiMo | `MIMO_API_KEY` | — | [指南](providers/mimo.md) |
| `xiaomi` | 小米 | `MIMO_API_KEY` | — | [指南](providers/xiaomi.md) |
| `siliconflow` | 硅基流动 | `SILICONFLOW_API_KEY` | `Qwen/Qwen3-8B` | [指南](providers/siliconflow.md) |
| `siliconrouter` | SiliconRouter | `SILICONROUTER_API_KEY` | — | [指南](providers/siliconrouter.md) |
| `dmxapi` | DMXAPI | `DMXAPI_API_KEY` | `gemini-2.5-flash` | [指南](providers/dmxapi.md) |
| `longcat` | 美团 LongCat | `LONGCAT_API_KEY` | `LongCat-Flash-Chat` | [指南](providers/longcat.md) |
| `yunwu` | 云雾 | `YUNWU_API_KEY` | `deepseek-chat` | [指南](providers/yunwu.md) |
| `ollama` | Ollama（本地） | `OLLAMA_BASE_URL` | `qwen3:30b` | [指南](providers/ollama.md) |
| `hermes_agent` | Hermes Agent | `HERMES_AGENT_BASE_URL` + `HERMES_AGENT_API_KEY` | `deepseek-v4-pro` | [指南](providers/hermes_agent.md) |
| `custom` | 自定义接口 | `CUSTOM_BASE_URL` + `CUSTOM_API_KEY` | 用户自定义 | [指南](providers/custom.md) |
| `openclaw` | OpenClaw 网关 | `OPENCLAW_BASE_URL` + `OPENCLAW_API_KEY` | 用户自定义 | [指南](providers/openclaw.md) |

## API 协议支持

| 协议 | 说明 |
|------|------|
| **Chat Completions** | `client.chat.completions.create()` — 所有提供商均原生支持 |
| **Responses API** | `client.responses.create()` — qwen/dashscope/dmxapi/hermes_agent/custom/openclaw 原生支持，其余通过内部自动转换 |
| **Embeddings** | `client.embeddings.create()` — 部分提供商支持 |

## 配置方式

每个指南都包含三种配置方式：
1. **环境变量** — 最简单，适合开发环境
2. **`provider_configs` 参数** — 代码内配置，适合多项目切换
3. **两者结合** — `provider_configs` 优先级高于环境变量
