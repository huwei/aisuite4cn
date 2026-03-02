import os

from aisuite4cn.base_provider import BaseProvider


class BaichuanProvider(BaseProvider):
    """
    Baichuan (百川智能) Provider
    Documentation: https://platform.baichuan-ai.com/docs/api
    """

    def __init__(self, **config):
        """
        Initialize the Baichuan provider with the given configuration.
        """
        current_config = dict(config)
        current_config.setdefault("api_key", os.getenv("BAICHUAN_API_KEY"))
        if not current_config.get("api_key"):
            raise ValueError(
                "Baichuan API key is missing. Please provide it in the config or set the BAICHUAN_API_KEY environment variable."
            )

        super().__init__("https://api.baichuan-ai.com/v1", **current_config)
