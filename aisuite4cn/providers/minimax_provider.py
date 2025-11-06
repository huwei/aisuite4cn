import os

from aisuite4cn.base_provider import BaseProvider


class MinimaxProvider(BaseProvider):
    """
    A provider for the DMXAPI API.
    """

    def __init__(self, **config):
        """
        Initialize the MiniMax provider with the given configuration.
        Pass the entire configuration dictionary to the MiniMax client constructor.
        """

        current_config = dict(config)
        current_config.setdefault("api_key", os.getenv("MINIMAX_API_KEY", None))
        if not current_config['api_key']:
            raise ValueError(
                "MiniMax API key is missing. Please provide it in the config or set the MINIMAX_API_KEY environment variable."
            )
        base_url = current_config.pop("base_url", os.getenv("MINIMAX_BASE_URL", 'https://api.minimaxi.com/v1'))
        super().__init__(base_url, **current_config)
