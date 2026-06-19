
import aisuite4cn as ai
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

client = ai.Client()

provider = "ollama"
model_id = "snowflake-arctic-embed-l-v2.0:latest"

response = client.embeddings.create(
    model=f"{provider}:{model_id}",
    input='你好'
)
print(response.data[0].embedding)



# model_id = "deepseek-r1:70b"
model_id = "qwen3:30b"

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "请模拟一下有思考模式输出的方式，要求先思考后回答。例如：<think>xxxx</think> xxxxx"},
]

response = client.chat.completions.create(
    model=f"{provider}:{model_id}",
    messages=messages,
    stream=True
)

# stream = true
is_first_conent = True
is_first_thinking = True
for chunk in response:
    if chunk.choices[0].delta.content:
        if is_first_conent:
            print("\ncontent:")
            is_first_conent = False
        print(chunk.choices[0].delta.content, end='')

    if hasattr(chunk.choices[0].delta, "reasoning_content") and chunk.choices[0].delta.reasoning_content:
        if is_first_thinking:
            print("\nthinking:")
            is_first_thinking = False
        print(chunk.choices[0].delta.reasoning_content, end='')

# stream = false

response = client.chat.completions.create(
    model=f"{provider}:{model_id}",
    messages=messages,
    stream=False
)

if hasattr(response.choices[0].message, "reasoning_content") and response.choices[0].message.reasoning_content:
    print('thinking:')
    print(response.choices[0].message.reasoning_content)
print('content:')
print(response.choices[0].message.content)
