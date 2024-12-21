import os

import zhipuai

from aisuite4cn.provider import Provider, LLMError


class ZhipuaiProvider(Provider):
    """
    Zhipu Provider
    """
    def __init__(self, **config):
        """
        Initialize the Zhipu provider with the given configuration.
        Pass the entire configuration dictionary to the Zhipu client constructor.
        """
        # Ensure API key is provided either in config or via environment variable

        self.config = dict(config)
        self.api_key = self.config.pop("api_key", None) or os.getenv("ZHIPUAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Zhipu API key is missing. Please provide it in the config or set the ZHIPUAI_API_KEY environment variable."
            )
        # Pass the entire config to the Zhipu client constructor
        self.client = zhipuai.ZhipuAI(
            api_key = self.api_key,
            **self.config)

    def chat_completions_create(self, model, messages, **kwargs):
        # Any exception raised by Zhipu will be returned to the caller.
        # Maybe we should catch them and raise a custom LLMError.
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs  # Pass any additional arguments to the Zhipu API
        )
