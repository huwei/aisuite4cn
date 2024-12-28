import openai
import os
from aisuite4cn.provider import Provider, LLMError


class DeepseekProvider(Provider):
    """
    DeepSeek Provider
    """
    def __init__(self, **config):
        """
        Initialize the DeepSeek provider with the given configuration.
        Pass the entire configuration dictionary to the DeepSeek client constructor.
        """
        # Ensure API key is provided either in config or via environment variable

        self.config = dict(config)
        self.api_key = self.config.pop("api_key", None) or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DeepSeek API key is missing. Please provide it in the config or set the DEEPSEEK_API_KEY environment variable."
            )
        # Pass the entire config to the DeepSeek client constructor
        self.client = openai.OpenAI(
            api_key = self.api_key,
            base_url = "https://api.deepseek.com/v1",
            **self.config)

    def chat_completions_create(self, model, messages, **kwargs):
        # Any exception raised by DeepSeek will be returned to the caller.
        # Maybe we should catch them and raise a custom LLMError.
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs  # Pass any additional arguments to the DeepSeek API
        )

