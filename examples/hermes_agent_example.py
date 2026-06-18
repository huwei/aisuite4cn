from dotenv import load_dotenv

import aisuite4cn as ai

# 加载 .env 文件中的环境变量
load_dotenv()

client = ai.Client()

provider = "hermes_agent"
model_id = "deepseek-v4-pro"

messages = [
    {"role": "user", "content": "我有哪些skill"},
]

# 流式调用
# hermes-agent 服务端会自主执行工具，hermes.tool.progress 事件会被
# 自动转换为 OpenAI 标准的 tool_calls 格式，客户端可以感知工具调用进度
print("=== 流式调用 ===")
response = client.chat.completions.create(
    model=f"{provider}:{model_id}",
    messages=messages,
    stream=True,
)

for chunk in response:
    choice = chunk.choices[0]
    delta = choice.delta
    # print(chunk)
    # 工具调用 — 来自 hermes.tool.progress 的转换

    if delta.tool_calls:
        for tc in delta.tool_calls:
            func = tc.function
            status = '完成' if choice.finish_reason == "tool_calls" else '进行中'
            print(f"\n[Tool #{tc.index+1}] {func.name}【{status}】")
            if func.name == "terminal":
                import json
                args = json.loads(func.arguments)
                print(f"  命令: {args.get('command', '')[:80]}")
            else:
                print(f"  参数: {func.arguments}")
    # 文本内容
    elif delta.content:
        print(delta.content, end="", flush=True)

print("\n")

# 非流式调用
# print("=== 非流式调用 ===")
# response = client.chat.completions.create(
#     model=f"{provider}:{model_id}",
#     messages=messages,
#     stream=False,
# )
# print(response.choices[0].message.content)
