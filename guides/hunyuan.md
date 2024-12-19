# Hunyuan（腾讯云混元大模型）

To use Hunyuan with `aisuite4cn`, you’ll need an [Tencent Cloud account](https://cloud.tencent.com/). 
After logging in, go to the [开通服务](https://console.cloud.tencent.com/hunyuan/settings) section to activate service.
After activating models service, go to the [API Keys](https://console.cloud.tencent.com/hunyuan/api-key) section in your account settings and generate a new key. 
Once you have your key, add it to your environment as follows:

```shell
export HUNYUAN_API_KEY="your-hunyuan-api-key"
```

## Create a Chat Completion

Install the `openai` Python client:

Example with pip:
```shell
pip install openai
```

Example with poetry:
```shell
poetry add openai
```

In your code:
```python
import aisuite4cn as ai
client = ai.Client()

provider = "hunyuan"
model_id = "hunyuan-pro"

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What’s the weather like in San Francisco?"},
]

response = client.chat.completions.create(
    model=f"{provider}:{model_id}",
    messages=messages,
)

print(response.choices[0].message.content)
```
