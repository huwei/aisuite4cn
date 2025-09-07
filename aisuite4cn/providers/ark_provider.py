import os

from aisuite4cn import BaseProvider


class ArkProvider(BaseProvider):
    """
    ByteDance Ark Provider
    """

    def __init__(self, **config):
        """
        Initialize the Volcengine provider with the given configuration.
        Pass the entire configuration dictionary to the Volcengine client constructor.
        """
        # Ensure API key is provided either in config or via environment variable
        current_config = dict(config)
        current_config.setdefault("api_key", os.getenv("ARK_API_KEY"))
        if not current_config["api_key"]:
            raise ValueError(
                "Ark API key is missing. Please provide it in the config or set the ARK_API_KEY environment variable."
            )

        super().__init__('https://ark.cn-beijing.volces.com/api/v3',
                         **current_config)
