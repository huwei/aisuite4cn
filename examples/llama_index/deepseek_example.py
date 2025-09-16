
from dotenv import load_dotenv
from aisuite4cn.llama_index import LlamaIndexClient

# 加载 .env 文件中的环境变量
load_dotenv()

provider = "deepseek"
model_id = "deepseek-reasoner"
# model_id = "deepseek-chat"


client = LlamaIndexClient(model=f"{provider}:{model_id}")


# resp = client.complete(model=f"{provider}:{model_id}", prompt="甲基丙烯酰化明胶的合成方案")
#
# print(resp.text)


resp = client.stream_complete(prompt="甲基丙烯酰化明胶的合成方案")
for chunk in resp:
    if hasattr(chunk.raw.choices[0].delta, 'reasoning_content') and chunk.raw.choices[0].delta.reasoning_content:
        print(chunk.raw.choices[0].delta.reasoning_content, end='')
    else:
        print(chunk.delta, end='')

#
# import asyncio
# # 方案1: 使用异步函数包装
# async def async_call():
#     resp = await client.acomplete(model="{provider}:{model_id}", prompt="根据用户的问题，输出回答内容，内容返回一个json字符串，包含answer字段")
#     print(resp.text)
#     return resp
#
# # 运行异步函数
# asyncio.run(async_call())