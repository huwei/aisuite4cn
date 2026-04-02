import os

from aisuite4cn.base_provider import BaseProvider


class MimoProvider(BaseProvider):
    """
    A provider for the Mimo API.
    """

    def __init__(self, **config):
        """
        Initialize the Mimo provider with the given configuration.
        Pass the entire configuration dictionary to the Mimo client constructor.
        """

        current_config = dict(config)
        current_config.setdefault("api_key", os.getenv("MIMO_API_KEY", None))
        if not current_config['api_key']:
            raise ValueError(
                "Mimo API key is missing. Please provide it in the config or set the MIMO_API_KEY environment variable."
            )
        base_url = current_config.pop("base_url", os.getenv("MIMO_API_KEY", 'https://api.xiaomimimo.com/v1'))
        super().__init__(base_url, **current_config)
