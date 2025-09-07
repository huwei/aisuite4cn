import os

from aisuite4cn.base_provider import BaseProvider


class SiliconflowProvider(BaseProvider):
    """
    Siliconflow Provider
    """

    def __init__(self, **config):
        """
        Initialize the Siliconflow provider with the given configuration.
        Pass the entire configuration dictionary to the Siliconflow client constructor.
        """
        # Ensure API key is provided either in config or via environment variable

        current_config = dict(config)
        current_config.setdefault("api_key", os.getenv("SILICONFLOW_API_KEY"))
        if not current_config['api_key']:
            raise ValueError(
                "Siliconflow API key is missing. Please provide it in the config or set the SILICONFLOW_API_KEY environment variable."
            )

        super().__init__(
            base_url='https://api.siliconflow.cn/v1',
            **current_config)
