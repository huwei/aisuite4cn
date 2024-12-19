import time

import openai
import os

from aisuite4cn.provider import Provider


class HunyuanProvider(Provider):
    """
    Tecent Hunyuan Provider

    API refer to: https://cloud.tencent.com/document/product/1729/111007
    """

    def __init__(self, **config):
        """
        Initialize the Hunyuan provider with the given configuration.
        Pass the entire configuration dictionary to the Hunyuan client constructor.
        """
        # Ensure access key and secret key is provided either in config or via environment variable

        self.config = dict(config)
        self.api_key = self.config.pop("api_key", None) or os.getenv("HUNYUAN_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Hunyuan api key is missing. Please provide it in the config or set the HUNYUAN_API_KEY environment variable."
            )
        # Pass the entire config to the Qianfan client constructor
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://api.hunyuan.cloud.tencent.com/v1",
            **self.config)

    def chat_completions_create(self, model, messages, **kwargs):
        # Any exception raised by Hunyuan will be returned to the caller.
        # Maybe we should catch them and raise a custom LLMError.
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs  # Pass any additional arguments to the Moonshot API
        )
