import openai
import os
from aisuite4cn.base_provider import BaseProvider


class LongcatProvider(BaseProvider):
    """
    Moonshot Provider
    """
    def __init__(self, **config):
        """
        Initialize the LongCat provider with the given configuration.
        Pass the entire configuration dictionary to the LongCat client constructor.
        """
        # Ensure API key is provided either in config or via environment variable

        current_config = dict(config)
        current_config.setdefault("api_key", os.getenv("LONGCAT_API_KEY"))
        if not current_config['api_key']:
            raise ValueError(
                "LongCat API key is missing. Please provide it in the config or set the LONGCAT_API_KEY environment variable."
            )

        super().__init__('https://api.longcat.chat/openai/v1',
                         **current_config)

