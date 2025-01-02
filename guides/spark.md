# Spark（讯飞开放平台，星火大模型）

To use Spark with `aisuite4cn`, you’ll need an [Spark account](https://passport.xfyun.cn/login). 
After logging in, go to the [My Apps](https://console.xfyun.cn/app/myapp) section your account settings and create a new app.
After create app, go to the [App API Center](https://console.xfyun.cn/services/sparkapiCenter) section in your account settings and generate a new key. 
Once you have your key, add it to your environment as follows:

```shell
export SPARK_API_KEY_MAP="4.0Ultra=APIPassword&generalv3=APIPassword"
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

provider = "spark"
model_id = "4.0Ultra"

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
