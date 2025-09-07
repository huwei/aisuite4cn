import os

from aisuite4cn.base_provider import BaseProvider


class OllamaProvider(BaseProvider):

    def __init__(self, **config):
        """
        Initialize the Ollama provider with the given configuration.
        Pass the entire configuration dictionary to the Ollama client constructor.
        """

        current_config = dict(config)

        base_url = current_config.pop("base_url", os.getenv("OLLAMA_BASE_URL"))
        current_config['api_key'] = current_config.get('api_key', os.getenv("OLLAMA_API_KEY",  "ollama"))
        # Pass the entire config to the Ollama client constructor
        super().__init__(base_url,
                         **current_config)
