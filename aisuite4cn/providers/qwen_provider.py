import openai
import os
from aisuite4cn.provider import Provider, LLMError


class QwenProvider(Provider):
    """
    阿里云大模型服务平台针对于千问大模型的提供者，使用了千问大模型兼容OpenAI的接口
    """
    def __init__(self, **config):
        """
        Initialize the Qwen shot provider with the given configuration.
        Pass the entire configuration dictionary to the Qwen client constructor.
        """
        # Ensure API key is provided either in config or via environment variable
        self.api_key = config.get("api_key") or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Dashscope API key is missing. Please provide it in the config or set the DASHSCOPE_API_KEY environment variable."
            )
        kvargs = dict(config)
        kvargs.pop("api_key")
        # Pass the entire config to the Qwen client constructor
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
            **kvargs)

    def chat_completions_create(self, model, messages, **kwargs):
        # Any exception raised by Qwen will be returned to the caller.
        # Maybe we should catch them and raise a custom LLMError.
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs  # Pass any additional arguments to the Qwen API
        )
