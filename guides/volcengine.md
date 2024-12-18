#  Volcengine AI（火山引擎方舟大模型服务平台）

To use Volcengine AI with `aisuite4cn`, you’ll need an [Volcengine account](https://console.volcengine.com/ark). 
After logging in, go to the [API Keys](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey) section in your account settings and generate a new key. 
Once you have your key, add it to your environment as follows:

```shell
export ARK_API_KEY="your-ark-api-key"
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

provider = "volcengine"
model_endpoint_id = "your-model-endpoint-id"

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What’s the weather like in San Francisco?"},
]

response = client.chat.completions.create(
    model=f"{provider}:{model_endpoint_id}",
    messages=messages,
)

print(response.choices[0].message.content)
```
