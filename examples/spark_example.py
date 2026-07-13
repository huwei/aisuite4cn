
import aisuite4cn as ai
from dotenv import load_dotenv

PROVIDER = "spark"
EMBEDDING_MODEL = "spark-mimo-embedding"
CHAT_MODEL = "4.0Ultra"


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
    """Chat Completions 流式输出"""
    print("\n" + "=" * 60)
    print("7. Chat Completions API - 流式输出")
    print("=" * 60)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "用一句话介绍一下Python"},
    ]
    response = client.chat.completions.create(
        model=f"{PROVIDER}:{CHAT_MODEL}",
        messages=messages,
        stream=True
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end='', flush=True)
    print()


def demo_chat_completions_non_stream(client):
    """Chat Completions 非流式输出"""
    print("\n" + "=" * 60)
    print("8. Chat Completions API - 非流式输出")
    print("=" * 60)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "用一句话介绍一下Python"},
    ]
    response = client.chat.completions.create(
        model=f"{PROVIDER}:{CHAT_MODEL}",
        messages=messages,
        stream=False
    )
    print(response.choices[0].message.content)


def main():
    load_dotenv()
    client = ai.Client()

    # Embeddings API
    demo_single_embedding(client)
    # demo_batch_embeddings(client)

    # Responses API
    # demo_responses_basic(client)
    # demo_responses_with_instructions(client)
    # demo_responses_stream(client)
    # demo_responses_multi_turn(client)
    #
    # Chat Completions API
    demo_chat_completions_stream(client)
    demo_chat_completions_non_stream(client)


if __name__ == "__main__":
    main()
