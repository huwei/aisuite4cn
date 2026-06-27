from dotenv import load_dotenv

import aisuite4cn as ai

# 加载 .env 文件中的环境变量
# 需要配置：
#   OPENCLAW_BASE_URL=http://<gateway-host>:<port>/v1
#   OPENCLAW_API_KEY=<gateway-token-or-password>   （gateway.auth.mode="none" 时可省略）
load_dotenv()

client = ai.Client()

provider = "openclaw"
# OpenClaw 将 OpenAI model 字段视为智能体目标，而非原始模型 ID：
#   "openclaw"           -> 路由到已配置的默认智能体
#   "openclaw/default"   -> 路由到默认智能体
#   "openclaw/<agentId>" -> 路由到特定智能体
model_id = "openclaw/default"

messages = [
    {"role": "user", "content": "你有哪些skill？"},
]


def chat_completions_stream():
    """
    流式调用（Chat Completions API）
    底层请求会作为普通 Gateway 网关智能体运行，与 openclaw agent 走相同代码路径。
    """
    print("=== 流式调用（Chat Completions API）===")
    response = client.chat.completions.create(
        model=f"{provider}:{model_id}",
        messages=messages,
        stream=True,
    )

    for chunk in response:
        print(chunk)
        # choice = chunk.choices[0]
        # delta = choice.delta
        #
        # if delta.tool_calls:
        #     for tc in delta.tool_calls:
        #         func = tc.function
        #         status = '完成' if choice.finish_reason == "tool_calls" else '进行中'
        #         print(f"\n[Tool #{tc.index + 1}] {func.name}【{status}】")
        #         if func.name == "terminal":
        #             import json
        #             args = json.loads(func.arguments)
        #             print(f"  命令: {args.get('command', '')[:80]}")
        #         else:
        #             print(f"  参数: {func.arguments}")
        # elif delta.content:
        #     print(delta.content, end="", flush=True)

    print("\n")


def chat_completions_non_stream():
    """
    非流式调用（Chat Completions API）
    """
    print("=== 非流式调用 ===")
    response = client.chat.completions.create(
        model=f"{provider}:{model_id}",
        messages=messages,
        stream=False,
    )
    print(response.choices[0].message.content)


def responses_stream():
    """
    Responses API 流式调用
    使用 Chat Completions → Responses API 适配器，
    将 OpenClaw 的 Chat Completions 响应转换为 Responses API 格式。
    tool_calls 会被转换为 ResponseFunctionToolCall 输出项，
    文本内容会被转换为 ResponseOutputMessage 输出项。
    """

    print("=== 流式调用（Responses API）===")

    response = client.responses.create(
        model=f"{provider}:{model_id}",
        input=messages[0]['content'],
        stream=True,
    )

    for event in response:
        event_type = event.type

        if event_type == "response.output_item.added":
            item = event.item
            if item.type == "function_call":
                print(f"\n[Tool] {item.name} 进行中")
                print(f"  call_id: {item.call_id}")

        elif event_type == "response.function_call_arguments.done":
            args_str = event.arguments
            print(f"  参数: {args_str}")

        elif event_type == "response.output_item.done":
            item = event.item
            if item.type == "function_call":
                status = item.status
                print(f"  状态: {status}")

        elif event_type == "response.reasoning_summary_text.delta":
            print(event.delta, end="", flush=True)

        elif event_type == "response.output_text.delta":
            print(event.delta, end="", flush=True)

        elif event_type == "response.completed":
            resp = event.response
            usage = resp.usage
            if usage:
                print(f"\n\n[完成] input_tokens={usage.input_tokens} output_tokens={usage.output_tokens}")

    print("\n")


if __name__ == "__main__":
    chat_completions_stream()
    # chat_completions_non_stream()
    # responses_stream()
