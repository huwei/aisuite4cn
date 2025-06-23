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

        self.base_url = self.config.pop("base_url", os.getenv("OLLAMA_BASE_URL"))
        self.config['api_key'] = self.config.get('api_key', os.getenv("OLLAMA_API_KEY",  "ollama"))
        # Pass the entire config to the Ollama client constructor
        self.client = openai.OpenAI(
            base_url=self.base_url,
            **self.config)

    def chat_completions_create(self, model, messages, **kwargs):

        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs  # Pass any additional arguments to the Ollama API
        )
