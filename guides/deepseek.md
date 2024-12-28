# Moonshot AI（月之暗面大模型开放平台）

To use DeepSeek with `aisuite4cn`, you’ll need an [DeepSeek account](https://platform.deepseek.com/). 
After logging in, go to the [API Keys](https://platform.deepseek.com/api_keys) section in your account settings and generate a new key. 
Once you have your key, add it to your environment as follows:

```shell
export DEEPSEEK_API_KEY="your-deepseek-api-key"
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

provider = "deepseek"
model_id = "deepseek-chat" 

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
