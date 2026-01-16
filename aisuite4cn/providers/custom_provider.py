import os

from aisuite4cn.base_provider import BaseProvider


class CustomProvider(BaseProvider):

    def __init__(self, **config):
        """
        Initialize the Custom provider with the given configuration.
        Pass the entire configuration dictionary to the Custom client constructor.
        """

        current_config = dict(config)

        base_url = current_config.pop("base_url", os.getenv("CUSTOM_BASE_URL"))
        if not base_url:
            raise ValueError(
                "Custom Base Url is missing. Please provide it in the config or set the CUSTOM_BASE_URL environment variable."
            )
        current_config['api_key'] = current_config.get('api_key', os.getenv("CUSTOM_API_KEY",  "custom"))
        # Pass the entire config to the Custom client constructor
        super().__init__(base_url, **current_config)
