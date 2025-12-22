import os

from aisuite4cn.base_provider import BaseProvider


class YunwuProvider(BaseProvider):
    """
    DeepSeek Provider
    """

    def __init__(self, **config):
        """
        Initialize the Yunwu.ai provider with the given configuration.
        Pass the entire configuration dictionary to the Yunwu client constructor.
        """
        # Ensure API key is provided either in config or via environment variable
        current_config = dict(config)
        current_config.setdefault("api_key", os.getenv("YUNWU_API_KEY"))
        if not current_config['api_key']:
            raise ValueError(
                "Yunwu.ai API key is missing. Please provide it in the config or set the YUNWU_API_KEY environment variable."
            )

        super().__init__('https://yunwu.ai/v1/',
                         **current_config)
