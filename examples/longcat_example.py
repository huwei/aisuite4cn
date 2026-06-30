import asyncio

from dotenv import load_dotenv

import aisuite4cn as ai

# 加载 .env 文件中的环境变量
load_dotenv()

client = ai.Client()

async_client = ai.AsyncClient()

provider = "longcat"
model_id = "LongCat-2.0"

messages = [
    {"role": "user", "content": "输出一个markdonw格式的说明"},
]

def chat_completions_stream():
    """
    流式调用（Chat Completions API）
    hermes-agent 服务端会自主执行工具，hermes.tool.progress 事件会被
    自动转换为 OpenAI 标准的 tool_calls 格式，客户端可以感知工具调用进度
    """
    print("=== 流式调用（Chat Completions API）===")
    response = client.chat.completions.create(
        model=f"{provider}:{model_id}",
        messages=messages,
        stream=True,
    )
    first_thinking = True
    for chunk in response:
        if not chunk.choices:
            continue
        choice = chunk.choices[0]
        delta = choice.delta

        if delta.tool_calls:
            for tc in delta.tool_calls:
                func = tc.function
                status = '完成' if choice.finish_reason == "tool_calls" else '进行中'
                print(f"\n[Tool #{tc.index + 1}] {func.name}【{status}】")
                if func.name == "terminal":
                    import json
                    args = json.loads(func.arguments)
                    print(f"  命令: {args.get('command', '')[:80]}")
                else:
                    print(f"  参数: {func.arguments}")
        elif delta.content:
            print(delta.content, end="", flush=True)
        elif hasattr(delta, 'reasoning_content'):
            if first_thinking:
                first_thinking = False
                print("\n[Thinking]")
            print(delta.reasoning_content, end="", flush=True)

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
    将 hermes-agent 的 Chat Completions 响应转换为 Responses API 格式。
    tool_calls 会被转换为 ResponseFunctionToolCall 输出项，
    文本内容会被转换为 ResponseOutputMessage 输出项。
    """

    print("=== 流式调用（Responses API）===")

    response = client.responses.create(
        model=f"{provider}:{model_id}",
        input=messages[0]['content'],
        thinking={'type': 'enabled'},
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
            import json
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
    responses_stream()
