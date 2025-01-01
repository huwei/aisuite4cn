from argparse import ArgumentError
from urllib.parse import parse_qs

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
        self.model_map:dict = self.config.get("model_map", None)
        env_dict = parse_qs(os.getenv("ARK_MODEL_MAP", ""))
        self.model_map = {k: v[0] for k, v in env_dict.items()}

        if not self.api_key:
            raise ValueError(
                "Ark API key is missing. Please provide it in the config or set the ARK_API_KEY environment variable."
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
            real_model = self.model_map.get(model, None)
            if real_model is None:
                raise ValueError("The model name must be the endpoint ID of the model.")
        else:
            real_model = model
        return self.client.chat.completions.create(
            model=real_model,
            messages=messages,
            **kwargs  # Pass any additional arguments to the Ark API
        )
