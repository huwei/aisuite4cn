
import aisuite4cn as ai
from dotenv import load_dotenv

PROVIDER = "ollama"
EMBEDDING_MODEL = "snowflake-arctic-embed-l-v2.0"
CHAT_MODEL = "qwen3:30b"


def demo_single_embedding(client):
    """单条文本向量化"""
    print("=" * 60)
    print("1. Embeddings API - 单条文本向量化")
    print("=" * 60)
    response = client.embeddings.create(
        model=f"{PROVIDER}:{EMBEDDING_MODEL}",
        input='你好'
    )
    print(f"向量维度: {len(response.data[0].embedding)}")
    print(f"前5个值: {response.data[0].embedding[:5]}")


def demo_batch_embeddings(client):
    """批量文本向量化"""
    print("\n" + "=" * 60)
    print("2. Embeddings API - 批量文本向量化")
    print("=" * 60)
    response = client.embeddings.create(
        model=f"{PROVIDER}:{EMBEDDING_MODEL}",
        input=['你好', '今天天气怎么样', 'Python是一种编程语言']
    )
    for i, item in enumerate(response.data):
        print(f"文本{i + 1} 向量维度: {len(item.embedding)}")


def demo_responses_basic(client):
    """Responses API 基础调用"""
    print("\n" + "=" * 60)
    print("3. Responses API - 基础调用")
    print("=" * 60)
    response = client.responses.create(
        model=f"{PROVIDER}:{CHAT_MODEL}",
        input="用一句话介绍一下Python"
    )
    print(f"响应ID: {response.id}")
    print(f"状态: {response.status}")
    print(f"输出: {response.output[0].content[0].text}")


def demo_responses_with_instructions(client):
    """Responses API 带系统指令"""
    print("\n" + "=" * 60)
    print("4. Responses API - 带系统指令")
    print("=" * 60)
    response = client.responses.create(
        model=f"{PROVIDER}:{CHAT_MODEL}",
        input="你好",
        instructions="你是一个专业的Python讲师，回答要简洁明了。"
    )
    for item in response.output:
        if hasattr(item, 'content') and item.content:
            print(f"输出: {item.content[0].text}")


def demo_responses_stream(client):
    """Responses API 流式输出"""
    print("\n" + "=" * 60)
    print("5. Responses API - 流式输出")
    print("=" * 60)
    for event in client.responses.create(
        model=f"{PROVIDER}:{CHAT_MODEL}",
        input="用Python写一个快速排序算法",
        stream=True
    ):
        if event.type == "response.output_text.delta":
            print(event.delta, end='', flush=True)
        elif event.type == "response.completed":
            print(f"\n\n完成! 使用了 {event.response.usage.output_tokens} 个输出token")


def demo_responses_multi_turn(client):
    """Responses API 多轮对话"""
    print("\n" + "=" * 60)
    print("6. Responses API - 多轮对话")
    print("=" * 60)
    response = client.responses.create(
        model=f"{PROVIDER}:{CHAT_MODEL}",
        input=[
            {"role": "system", "content": "你是一个乐于助人的助手。"},
            {"role": "user", "content": "1+1等于几？"},
        ]
    )
    for item in response.output:
        if hasattr(item, 'content') and item.content:
            print(f"回复: {item.content[0].text}")


def demo_chat_completions_stream(client):
    """Chat Completions 推理模型流式输出"""
    print("\n" + "=" * 60)
    print("7. Chat Completions API - 推理模型（流式）")
    print("=" * 60)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "请模拟一下有思考模式输出的方式，要求先思考后回答。例如：<think>xxxx</think> xxxxx"},
    ]
    response = client.chat.completions.create(
        model=f"{PROVIDER}:{CHAT_MODEL}",
        messages=messages,
        stream=True
    )
    is_first_content = True
    is_first_thinking = True
    for chunk in response:
        if chunk.choices[0].delta.content:
            if is_first_content:
                print("\ncontent:")
                is_first_content = False
            print(chunk.choices[0].delta.content, end='')
        if hasattr(chunk.choices[0].delta, "reasoning_content") and chunk.choices[0].delta.reasoning_content:
            if is_first_thinking:
                print("\nthinking:")
                is_first_thinking = False
            print(chunk.choices[0].delta.reasoning_content, end='')


def demo_chat_completions_non_stream(client):
    """Chat Completions 推理模型非流式输出"""
    print("\n\n" + "=" * 60)
    print("8. Chat Completions API - 推理模型（非流式）")
    print("=" * 60)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "请模拟一下有思考模式输出的方式，要求先思考后回答。例如：<think>xxxx</think> xxxxx"},
    ]
    response = client.chat.completions.create(
        model=f"{PROVIDER}:{CHAT_MODEL}",
        messages=messages,
        stream=False
    )
    if hasattr(response.choices[0].message, "reasoning_content") and response.choices[0].message.reasoning_content:
        print('thinking:')
        print(response.choices[0].message.reasoning_content)
    print('content:')
    print(response.choices[0].message.content)


def main():
    load_dotenv()
    client = ai.Client()

    # Embeddings API
    demo_single_embedding(client)
    # demo_batch_embeddings(client)

    # # Responses API
    # demo_responses_basic(client)
    # demo_responses_with_instructions(client)
    # demo_responses_stream(client)
    # demo_responses_multi_turn(client)
    #
    # # Chat Completions API
    # demo_chat_completions_stream(client)
    # demo_chat_completions_non_stream(client)


if __name__ == "__main__":
    main()
