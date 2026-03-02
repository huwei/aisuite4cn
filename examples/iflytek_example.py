"""iFlytek (讯飞星火) Example for aisuite4cn.

Before running, set your API key:
    export IFLYTEK_API_KEY="your-key"
"""

import aisuite4cn as ai


def iflytek_example():
    """Example using iFlytek (讯飞星火)."""
    print("\n=== iFlytek (讯飞星火) Example ===")
    
    client = ai.Client()
    
    # iFlytek Spark models
    models = [
        "iflytek:spark-v3.5",
        "iflytek:spark-v3",
        "iflytek:spark-v2",
    ]
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "请介绍一下讯飞星火大模型的特点。"},
    ]
    
    for model in models:
        try:
            print(f"\nModel: {model}")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
            )
            print(f"Response: {response.choices[0].message.content}")
        except Exception as e:
            print(f"Error with {model}: {e}")


if __name__ == "__main__":
    iflytek_example()
