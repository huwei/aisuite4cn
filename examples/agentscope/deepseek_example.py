import asyncio
import json

from agentscope.agent import ReActAgent, UserAgent
from agentscope.memory import InMemoryMemory
from agentscope.message import Msg
from agentscope.tool import Toolkit
from dotenv import load_dotenv

from aisuite4cn.agentscope import AgentScopeClient, OpenAICompatibleFormatter
from aisuite4cn.agentscope._openai_compatible_formatter import OpenAICompatibleMultiAgentFormatter

# 加载 .env 文件中的环境变量
load_dotenv()

provider = "deepseek"
model_id = "deepseek-chat"

friday = ReActAgent(
    name="Friday",
    sys_prompt="You're a helpful assistant named Friday",
    model=AgentScopeClient(
        model_name=f"{provider}:{model_id}"
    ),
    formatter=OpenAICompatibleFormatter(),  # The formatter for user-agent conversation
    memory=InMemoryMemory(),
    toolkit=Toolkit(),
)

# Create a user agent
user = UserAgent(name="User")


# async def run_conversation() -> None:
#     """Run a simple conversation between Friday and User."""
#     msg = None
#     while True:
#         msg = await friday(msg)
#         msg = await user(msg)
#         if msg.get_text_content() == "exit":
#             break
#
#
# asyncio.run(run_conversation())


async def example_multi_agent_prompt() -> None:
    msgs = [
        Msg("system", "You're a helpful assistant named Bob.", "system"),
        Msg("Alice", "Hi!", "user"),
        Msg("Bob", "Hi! Nice to meet you guys.", "assistant"),
        Msg("Charlie", "Me too! I'm Charlie, by the way.", "assistant"),
    ]

    formatter = OpenAICompatibleMultiAgentFormatter()
    prompt = await formatter.format(msgs)

    print("Formatted prompt:")
    print(json.dumps(prompt, indent=4, ensure_ascii=False))

    # We print the content of the combined user message here for better
    # understanding:
    print("-------------")
    print("Combined message")
    print(prompt[1]["content"])


asyncio.run(example_multi_agent_prompt())
