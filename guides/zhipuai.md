# 智普（智普AI大模型）

To use zhipu with `aisuite4cn`, you’ll need an [zhipu account](https://open.bigmodel.cn/). 
After logging in, go to the [API Keys](https://open.bigmodel.cn/usercenter/proj-mgmt/apikeys) section in your account settings and generate a new key. 
Once you have your key, add it to your environment as follows:

```shell
export ZHIPUAI_API_KEY="your-zhipuai-api-key"
```

## Create a Chat Completion

Install the `zhipuai` Python client:

Example with pip:
```shell
pip install zhipuai
```

Example with poetry:
```shell
poetry add zhipuai
```

In your code:
```python
import aisuite4cn as ai
client = ai.Client()

provider = "zhipuai"
model_id = "glm-4-flash"

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
