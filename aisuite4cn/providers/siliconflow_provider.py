import os

import openai

from aisuite4cn.provider import Provider


class SiliconflowProvider(Provider):
    """
    Siliconflow Provider
    """

    def __init__(self, **config):
        """
        Initialize the Siliconflow provider with the given configuration.
        Pass the entire configuration dictionary to the Siliconflow client constructor.
        """
        # Ensure API key is provided either in config or via environment variable

        self.config = dict(config)
        self.config.setdefault("api_key", os.getenv("SILICONFLOW_API_KEY"))
        if not self.config['api_key']:
            raise ValueError(
                "Siliconflow API key is missing. Please provide it in the config or set the SILICONFLOW_API_KEY environment variable."
            )
        # Pass the entire config to the DeepSeek client constructor
        self.client = openai.OpenAI(
            base_url="https://api.siliconflow.cn/v1",
            **self.config)

    def chat_completions_create(self, model, messages, **kwargs):

        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs  # Pass any additional arguments to the Siliconflow API
        )