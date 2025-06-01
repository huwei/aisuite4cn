
import aisuite4cn as ai
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

client = ai.Client()

provider = "ollama"
# model_id = "deepseek-r1:70b"
model_id = "qwen2.5:72b"

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What’s the weather like in San Francisco?"},
]

response = client.chat.completions.create(
    model=f"{provider}:{model_id}",
    messages=messages,
    stream=True
)

# stream = true

for chunk in response:

    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end='')

# stream = false

response = client.chat.completions.create(
    model=f"{provider}:{model_id}",
    messages=messages,
    stream=False
)

print('content:')
print(response.choices[0].message.content)
