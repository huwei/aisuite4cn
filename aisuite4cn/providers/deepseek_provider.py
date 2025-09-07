import os

from aisuite4cn.base_provider import BaseProvider


class DeepseekProvider(BaseProvider):
    """
    DeepSeek Provider
    """

    def __init__(self, **config):
        """
        Initialize the DeepSeek provider with the given configuration.
        Pass the entire configuration dictionary to the DeepSeek client constructor.
        """
        # Ensure API key is provided either in config or via environment variable
        current_config = dict(config)
        current_config.setdefault("api_key", os.getenv("DEEPSEEK_API_KEY"))
        if not current_config['api_key']:
            raise ValueError(
                "DeepSeek API key is missing. Please provide it in the config or set the DEEPSEEK_API_KEY environment variable."
            )

        super().__init__('https://api.deepseek.com/v1',
                         **current_config)
