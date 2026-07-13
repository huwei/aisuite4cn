
import aisuite4cn as ai
from dotenv import load_dotenv

PROVIDER = "custom"
CHAT_MODEL = "your-model-name"


def demo_chat_completions_stream(client):
    """Chat Completions 流式输出"""
    print("=" * 60)
    print("1. Chat Completions API - 流式输出")
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
    print("2. Chat Completions API - 非流式输出")
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

    demo_chat_completions_stream(client)
    demo_chat_completions_non_stream(client)


if __name__ == "__main__":
    main()
