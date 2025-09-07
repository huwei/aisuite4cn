import openai
import os
from aisuite4cn.base_provider import BaseProvider


class MoonshotProvider(BaseProvider):
    """
    Moonshot Provider
    """
    def __init__(self, **config):
        """
        Initialize the Moonshot provider with the given configuration.
        Pass the entire configuration dictionary to the Moonshot client constructor.
        """
        # Ensure API key is provided either in config or via environment variable

        current_config = dict(config)
        current_config.setdefault("api_key", os.getenv("MOONSHOT_API_KEY"))
        if not current_config['api_key']:
            raise ValueError(
                "Moonshot API key is missing. Please provide it in the config or set the MOONSHOT_API_KEY environment variable."
            )

        super().__init__('https://api.moonshot.cn/v1',
                         **current_config)

