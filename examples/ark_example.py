
import aisuite4cn as ai
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

client = ai.Client()

provider = "ark"
model_id = "doubao-seed-1.6-250615"

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What’s the weather like in San Francisco?"},
]

response = client.chat.completions.create(
    model=f"{provider}:{model_id}",
    messages=messages,
    stream=True,
    temperature=1,
    max_tokens=16000,
    thinking={"type": "disabled"}
)

# stream = true

for chunk in response:

    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end='')

# stream = false

response = client.chat.completions.create(
    model=f"{provider}:{model_id}",
    messages=messages,
    stream=False,
    temperature=1,
    max_tokens=16000,
    thinking={"type": "disabled"}
)

print('content:')
print(response.choices[0].message.content)
