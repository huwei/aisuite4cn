# Qianfan （百度千帆大模型服务平台）


Used the Qianfan V2 API, supporting models refer to [对话Chat V2](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Wm3fhy2vb).

To use Qianfan with `aisuite4cn`, you’ll need an [Qianfan account](https://login.bce.baidu.com/?_=1734615619743&redirect=https%3A%2F%2Fconsole.bce.baidu.com%2Fiam%2F#/iam/baseinfo). 
After logging in, go to the [安全认证](https://console.bce.baidu.com/iam/#/iam/accesslist) section in your account settings and generate a new key. 
Once you have your `access-key` and `secret-key`, add it to your environment as follows:

```shell
export QIANFAN_ACCESS_KEY="your-qianfan-access-key"
export QIANFAN_SECRET_KEY="your-qianfan-secret-key"
```

## Create a Chat Completion

Install the `qianfan` Python client:

Example with pip:
```shell
pip install qianfan
```

Example with poetry:
```shell
poetry add qianfan
```

In your code:
```python
import aisuite4cn as ai
client = ai.Client()

provider = "qianfan"
model_id = "ernie-3.5-8k" 

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
