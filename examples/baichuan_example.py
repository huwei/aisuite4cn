import aisuite4cn as ai

from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()


def baichuan_example():
    """Example using Baichuan AI."""
    print("=== Baichuan (百川) Example ===")

    # Initialize client
    client = ai.Client()

    # Baichuan models
    models = [
        "baichuan:Baichuan4",
        "baichuan:Baichuan3-Turbo",
        "baichuan:Baichuan3-Turbo-128k",
    ]

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你好，请介绍一下你自己。"},
    ]

    for model in models:
        try:
            print(f"\nModel: {model}")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
            )
            print(f"Response: {response.choices[0].message.content}")
        except Exception as e:
            print(f"Error with {model}: {e}")


if __name__ == "__main__":
    baichuan_example()
