from argparse import ArgumentError

import openai
import os
from aisuite4cn.provider import Provider, LLMError


class ArkProvider(Provider):
    """
    ByteDance Ark Provider
    """
    def __init__(self, **config):
        """
        Initialize the Volcengine provider with the given configuration.
        Pass the entire configuration dictionary to the Volcengine client constructor.
        """
        # Ensure API key is provided either in config or via environment variable
        self.config = dict(config)
        self.api_key = self.config.pop("api_key", None) or os.getenv("ARK_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Ark API key is missing. Please provide it in the config or set the OPENAI_API_KEY environment variable."
            )
        # Pass the entire config to the Ark client constructor

        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            **self.config)

    def chat_completions_create(self, model, messages, **kwargs):

        # Any exception raised by Ark will be returned to the caller.
        # Maybe we should catch them and raise a custom LLMError.

        if not model.startswith("ep-"):
            raise ValueError("The model name must be the endpoint ID of the model.")
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs  # Pass any additional arguments to the Ark API
        )
