from dotenv import load_dotenv

import aisuite4cn as ai

# 加载 .env 文件中的环境变量
load_dotenv()

client = ai.Client()

provider = "deepseek"
model_id = "deepseek-reasoner"
# model_id = "deepseek-chat"

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

# stream = False
#
# response = client.chat.completions.create(
#     model=f"{provider}:{model_id}",
#     messages=messages,
#     stream=False,
#     response_format={
#         "type": "json_object"
#     }
# )
#
# print(response.choices[0].message.content)
