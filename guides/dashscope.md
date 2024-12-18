#  Qwen (阿里千问大模型)

To use Qwen with `aisuite4cn`, you’ll need an [aliyun account](https://account.console.aliyun.com/). 
After logging in, go to the [API Keys](https://bailian.console.aliyun.com/?apiKey=1#/api-key-center) section in your account settings and generate a new key. 
Once you have your key, add it to your environment as follows:

```shell
export DASHSCOPE_API_KEY="your-dashscope-api-key"
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

provider = "qwen"
model_id = "your-model-id"

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
