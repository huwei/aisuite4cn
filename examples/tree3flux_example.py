import aisuite4cn as ai
from dotenv import load_dotenv

# Tree3-Flux 是一个 OpenAI 兼容的聚合网关，支持平台已开通的各类模型。
# 使用前请设置环境变量：TREE3FLUX_API_KEY=<your-tree3flux-api-key>
# 可用模型可通过 https://ai.zoomsys.com.cn/api/pricing 查看，
# 或按需替换为你的账号已开通的模型 ID。
PROVIDER = "tree3flux"
CHAT_MODEL = "deepseek-v4-1-flash-260910"

# 说明：当前 Tree3-Flux 模型列表中未提供 embedding 模型，
# 如后续开通，可将其替换为对应模型 ID 后再运行向量化示例。
EMBEDDING_MODEL = "text-embedding-3-small"


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
            usage = event.response.usage
            if usage is not None:
                print(f"\n\n完成! 使用了 {usage.output_tokens} 个输出token")
            else:
                print("\n\n完成!")


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
        if chunk.choices and chunk.choices[0].delta.content:
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

    # Embeddings API（当前平台未提供 embedding 模型，如已开通可取消注释）
    # demo_single_embedding(client)
    # demo_batch_embeddings(client)

    # Responses API
    # demo_responses_basic(client)
    # demo_responses_with_instructions(client)
    demo_responses_stream(client)
    # demo_responses_multi_turn(client)

    # Chat Completions API
    # demo_chat_completions_non_stream(client)
    # demo_chat_completions_stream(client)


if __name__ == "__main__":
    main()