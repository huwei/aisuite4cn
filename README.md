# aisuite4cn

[![PyPI](https://img.shields.io/pypi/v/aisuite4cn)](https://pypi.org/project/aisuite4cn/)

简单、统一的接口，可连接多个生成式人工智能提供商。

`aisuite4cn` 针对于中国的各类大模型厂商提供通用的支持。学习了`aisuite`方案，并开发了该库。

`aisuite4cn` 使得开发者能够通过标准化的接口轻松使用多个大型语言模型（LLM）。使用类似于OpenAI的接口，`aisuite4cn` 使得与最受欢迎的LLM互动并比较结果变得简单。它是Python客户端库的轻量级包装器，允许创造者在不改变代码的情况下无缝切换并测试来自不同LLM提供商的响应。我们将在不久的将来扩展它以覆盖更多的用例。

当前支持的提供商包括：
Moonshot（月之暗面）、
Doubao（火山引擎方舟大模型服务平台）、
Qwen（阿里云千问大模型）、
Hunyuan（腾讯混元大模型）、
Ernie（百度文心一言）、
ZhipuAI（BigModel智谱AI大模型开放平台）


## 安装

你可以只安装基础的 `aisuite4cn` 包，这只会安装基础包，而不会安装任何提供商的SDK。
或者同时安装某个提供商的包和 `aisuite4cn`包。

请注意，在 create() 调用中的模型名称使用格式为 `<provider>:<model-name>`。 
`aisuite4cn` 将根据提供商值调用相应的提供商并传递正确的参数。 
提供商的列表可以在目录 `aisuite4cn/providers/` 中找到。
支持的提供商的格式为该目录下的 `<provider>_provider.py`。

```shell
pip install aisuite4cn
```

安装通义千问大模型供应商的包

```shell
pip install 'aisuite4cn[qwen]'
```

安装所有大模型供应商的包

```shell
pip install 'aisuite4cn[all]'
```

## 配置
你需要为你打算使用的提供商获取 API 密钥。你需要单独安装或在安装 `aisuite4cn` 时安装特定提供商的库。
API 密钥可以设置为环境变量，也可以作为配置传递给 `aisuite4cn` 客户端构造函数。你可以使用工具如 `python-dotenv` 或 `direnv` 来手动设置环境变量。
以下是一个简短的示例，展示如何使用 `aisuite4cn` 从 qwen 和 moonshot 生成聊天完成响应。

设置API keys.

```shell
export MOONSHOT_API_KEY="your-moonshot-api-key" # 月之暗面开放平台api-key，支持moonshot
export DASHSCOPE_API_KEY="your-dashscope-api-key" # 百炼平台api-key，支持qwen
export ARK_API_KEY = "your-ark-api-key" #火山引擎api-key，支持doubao
export HUNYUAN_API_KEY = "your-hunyuan-api-key" #腾讯混元api-key，支持混元
export ZHIPUAI_API_KEY = "your-zhipuai-api-key" #智谱AI api-key，支持ChatGLM
export QIANFAN_ACCESS_KEY = "your-qianfan-access-key" #百度千帆 access key，支持文心一言
export QIANFAN_SECRET_KEY = "your-qianfan-secret-key" #百度千帆 secret key，支持文心一言
export DEEPSEEK_API_KEY="your-deepseek-api-key" # deepseek开放平台api-key，支持deepseek
```

使用python客户端
```python
import aisuite4cn as ai
client = ai.Client()

models = ["qwen:qwen-max", 
          "ark:your-model-endpoint-id",
          "moonshot:moonshot-v1-8k",
          "hunyuan:hunyuan-standard",
          "qianfan:ernie-3.5-8k",
          "zhipuai:glm-4-flash",
          "deepseek:deepseek-chat",
          ]

messages = [
    {"role": "system", "content": "Respond in Pirate English."},
    {"role": "user", "content": "Tell me a joke."},
]

for model in models:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.75
    )
    print(response.choices[0].message.content)

```

## License
`aisuite4cn` 在 MIT 许可证下发布。您可以自由地将代码用于商业和非商业目的。


## Integrated Open source project
Special thanks to all contributors

### aisuite
https://github.com/andrewyng/aisuite

### openai-python
https://github.com/openai/openai-python
