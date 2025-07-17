import os

import openai
from volcenginesdkarkruntime import Ark

from aisuite4cn.provider import Provider


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
        self.config.setdefault("api_key", os.getenv("ARK_API_KEY"))
        if not self.config["api_key"]:
            raise ValueError(
                "Ark API key is missing. Please provide it in the config or set the ARK_API_KEY environment variable."
            )
        # Pass the entire config to the Ark client constructor
        self.client = Ark(**self.config)

    def chat_completions_create(self, model, messages, **kwargs):

        # Any exception raised by Ark will be returned to the caller.
        # Maybe we should catch them and raise a custom LLMError.

        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs  # Pass any additional arguments to the Ark API
        )
