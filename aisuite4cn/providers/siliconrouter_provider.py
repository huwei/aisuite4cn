import os

from aisuite4cn.base_provider import BaseProvider


class SiliconrouterProvider(BaseProvider):
    """
    A provider for the SiliconRouter API.
    """

    def __init__(self, **config):
        """
        Initialize the SiliconRouter provider with the given configuration.
        Pass the entire configuration dictionary to the SiliconRouter client constructor.
        """

        current_config = dict(config)
        current_config.setdefault("api_key", os.getenv("SILICONROUTER_API_KEY", None))
        if not current_config['api_key']:
            raise ValueError(
                "SiliconRouter API key is missing. Please provide it in the config or set the SILICONROUTER_API_KEY environment variable."
            )
        base_url = current_config.pop("base_url", os.getenv("SILICONROUTER_API_KEY", 'https://api.siliconrouter.com/v1'))
        super().__init__(base_url, **current_config)
