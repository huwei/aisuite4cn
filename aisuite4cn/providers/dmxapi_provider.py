import os

import openai

from aisuite4cn.provider import Provider


class DmxapiProvider(Provider):
    """
    A provider for the DMXAPI API.
    """

    def __init__(self, **config):
        """
        Initialize the Dmxapi provider with the given configuration.
        Pass the entire configuration dictionary to the Dmxapi client constructor.
        """

        self.config = dict(config)

        self.base_url = self.config.pop("base_url", 'https://www.dmxapi.com/v1/')
        self.config['api_key'] = self.config.get('api_key', os.getenv("DMXAPI_API_KEY", None))
        if not self.config['api_key']:
            raise ValueError(
                "Dmxapi API key is missing. Please provide it in the config or set the DMXAPI_API_KEY environment variable."
            )
        # Pass the entire config to the Dmxapi client constructor
        self.client = openai.OpenAI(
            base_url=self.base_url,
            **self.config)

    def chat_completions_create(self, model, messages, **kwargs):

        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs  # Pass any additional arguments to the Dmxapi API
        )
