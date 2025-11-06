# -*- coding: utf-8 -*-
from dotenv import load_dotenv

import aisuite4cn as ai

# 加载 .env 文件中的环境变量
load_dotenv()

client = ai.Client()

provider = "minimax"
model_id = "MiniMax-M2"

response = client.chat.completions.create(
    model=f"{provider}:{model_id}",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hi, how are you?"},
    ],
    # 设置 reasoning_split=True 将思考内容分离到 reasoning_details 字段
    extra_body={"reasoning_split": True},
)

print(f"Thinking:\n{response.choices[0].message.reasoning_details[0]['text']}\n")
print(f"Text:\n{response.choices[0].message.content}\n")