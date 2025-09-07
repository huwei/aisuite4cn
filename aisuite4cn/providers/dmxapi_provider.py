import os

from aisuite4cn.base_provider import BaseProvider


class DmxapiProvider(BaseProvider):
    """
    A provider for the DMXAPI API.
    """

    def __init__(self, **config):
        """
        Initialize the Dmxapi provider with the given configuration.
        Pass the entire configuration dictionary to the Dmxapi client constructor.
        """

        current_config = dict(config)
        current_config.setdefault("api_key", os.getenv("DMXAPI_API_KEY", None))
        if not current_config['api_key']:
            raise ValueError(
                "Dmxapi API key is missing. Please provide it in the config or set the DMXAPI_API_KEY environment variable."
            )
        base_url = current_config.pop("base_url", os.getenv("DMXAPI_BASE_URL", 'https://www.dmxapi.cn/v1/'))
        super().__init__(base_url, **current_config)
