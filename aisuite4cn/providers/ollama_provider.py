import os

import openai

from aisuite4cn.provider import Provider


class OllamaProvider(Provider):

    def __init__(self, **config):
        """
        Initialize the Ollama provider with the given configuration.
        Pass the entire configuration dictionary to the Ollama client constructor.
        """

        self.config = dict(config)
        self.config['api_key'] = "ollama"

        self.base_url = self.config.pop("base_url", os.getenv("OLLAMA_BASE_URL"))
        # Pass the entire config to the DeepSeek client constructor
        self.client = openai.OpenAI(
            base_url=self.base_url,
            **self.config)

    def chat_completions_create(self, model, messages, **kwargs):

        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs  # Pass any additional arguments to the Moonshot API
        )
