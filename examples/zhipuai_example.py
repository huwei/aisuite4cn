import asyncio

from dotenv import load_dotenv

import aisuite4cn as ai

# 加载 .env 文件中的环境变量
load_dotenv()

provider = "zhipuai"
model_id = "embedding-3"

client = ai.Client()

async_client = ai.AsyncClient()

response = client.embeddings.create(
    model=f"{provider}:{model_id}",
    input='你好'
)
print(response.data[0].embedding)


model_id = "glm-4-flash"

messages = [
    {"role": "system", "content": "根据用户的问题，输出回答内容，内容返回一个json字符串，包含answer字段"},
    {"role": "user", "content": "who are you"},
]

# stream = True
response = client.chat.completions.create(
    model=f"{provider}:{model_id}",
    messages=messages,
    stream=True,
    response_format={
        "type": "json_object"
    }
)

for chunk in response:

    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end='')

async def async_create():

    response = await async_client.chat.completions.create(
        model=f"{provider}:{model_id}",
        messages=messages,
        stream=True,
        response_format={
            "type": "json_object"
        }
    )

    async for chunk in response:

        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end='')

asyncio.run(async_create())

# stream = False

response = client.chat.completions.create(
    model=f"{provider}:{model_id}",
    messages=messages,
    stream=False,
    response_format={
        "type": "json_object"
    }
)

print(response.choices[0].message.content)
