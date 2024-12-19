import openai
import os
from aisuite4cn.provider import Provider, LLMError


class MoonshotProvider(Provider):
    """
    Moonshot Provider
    """
    def __init__(self, **config):
        """
        Initialize the Moonshot provider with the given configuration.
        Pass the entire configuration dictionary to the Moonshot client constructor.
        """
        # Ensure API key is provided either in config or via environment variable

        self.config = dict(config)
        self.api_key = self.config.pop("api_key", None) or os.getenv("MOONSHOT_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Moonshot API key is missing. Please provide it in the config or set the MOONSHOT_API_KEY environment variable."
            )
        # Pass the entire config to the Moonshot client constructor
        self.client = openai.OpenAI(
            api_key = self.api_key,
            base_url = "https://api.moonshot.cn/v1",
            **self.config)

    def chat_completions_create(self, model, messages, **kwargs):
        # Any exception raised by Moonshot will be returned to the caller.
        # Maybe we should catch them and raise a custom LLMError.
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs  # Pass any additional arguments to the Moonshot API
        )

