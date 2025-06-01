
import aisuite4cn as ai
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

client = ai.Client()

provider = "deepseek"
model_id = "deepseek-reasoner"
# model_id = "deepseek-chat"

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

    if chunk.choices[0].delta.reasoning_content:
        print(chunk.choices[0].delta.reasoning_content, end='')

    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end='')

# stream = false

response = client.chat.completions.create(
    model=f"{provider}:{model_id}",
    messages=messages,
    stream=False
)

print('reasoning_content:')
print(response.choices[0].message.reasoning_content)
print('content:')
print(response.choices[0].message.content)
