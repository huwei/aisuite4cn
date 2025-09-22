
import os
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from aisuite4cn.langchain.langchain_client import LangchainClient


# 1. 定义你的 Pydantic 模型
class Joke(BaseModel):
    setup: str = Field(description="笑话的铺垫部分")
    punchline: str = Field(description="笑话的点睛之笔")

# 2. 初始化模型和 Pydantic 解析器
model = LangchainClient(model="deepseek:deepseek-chat")
parser = PydanticOutputParser(pydantic_object=Joke)

# 3. 创建一个提示模板，并注入格式化指令
# parser.get_format_instructions() 会生成一段文本，告诉模型如何格式化其输出
prompt_template = """
请根据用户的问题回答。
{format_instructions}

用户问题: {query}
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# 4. 使用 LangChain 表达式语言 (LCEL) 组装链
# 管道符 | 表示将前一步的输出作为后一步的输入
chain = prompt | model | parser

# 5. 调用链
query = "给我讲一个关于程序员的笑话"
joke_object: Joke = chain.invoke(
    input={"query": query},
    model="deepseek:deepseek-chat"
)

# 6. 验证返回值的类型
print(f"Returned object type: {type(joke_object)}")
# > Returned object type: <class '__main__.Joke'>

# 7. 使用结构化数据
print("--- 笑话时间 ---")
print(f"铺垫: {joke_object.setup}")
print(f"笑点: {joke_object.punchline}")
# > --- 笑话时间 ---
# > 铺垫: 为什么程序员总是分不清万圣节和圣诞节？
# > 笑点: 因为 Oct 31 == Dec 25！ (八进制的31等于十进制的25)
