import asyncio

from dotenv import load_dotenv

import aisuite4cn as ai

# 加载 .env 文件中的环境变量
load_dotenv()

provider = "siliconflow"
model_id = "BAAI/bge-m3"

client = ai.Client()

# stream = True
response = client.embeddings.create(
    model=f"{provider}:{model_id}",
    input='你好'
)

print(response.data[0].embedding)



async_client = ai.AsyncClient()

async def async_create():
    response = await async_client.embeddings.create(
        model=f"{provider}:{model_id}",
        input='你好'
    )
    print(response.data[0].embedding)

asyncio.run(async_create())