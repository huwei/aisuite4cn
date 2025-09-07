import asyncio

from agentscope.agent import ReActAgent, UserAgent
from agentscope.formatter import (
    OpenAIChatFormatter,
)
from agentscope.memory import InMemoryMemory
from agentscope.tool import Toolkit
from dotenv import load_dotenv

from aisuite4cn.agentscope import AgentScopeClient

# 加载 .env 文件中的环境变量
load_dotenv()

friday = ReActAgent(
    name="Friday",
    sys_prompt="You're a helpful assistant named Friday",
    model=AgentScopeClient(
        model_name="deepseek:deepseek-chat"
    ),
    formatter=OpenAIChatFormatter(),  # The formatter for user-agent conversation
    memory=InMemoryMemory(),
    toolkit=Toolkit(),
)

# Create a user agent
user = UserAgent(name="User")


async def run_conversation() -> None:
    """Run a simple conversation between Friday and User."""
    msg = None
    while True:
        msg = await friday(msg)
        msg = await user(msg)
        if msg.get_text_content() == "exit":
            break


asyncio.run(run_conversation())
