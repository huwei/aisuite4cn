import os

from aisuite4cn.base_provider import BaseProvider


class HunyuanProvider(BaseProvider):
    """
    Tecent Hunyuan Provider

    API refer to: https://cloud.tencent.com/document/product/1729/111007
    """

    def __init__(self, **config):
        """
        Initialize the Hunyuan provider with the given configuration.
        Pass the entire configuration dictionary to the Hunyuan client constructor.
        """
        # Ensure access key and secret key is provided either in config or via environment variable

        current_config = dict(config)
        current_config.setdefault("api_key", os.getenv("HUNYUAN_API_KEY"))
        if not current_config['api_key']:
            raise ValueError(
                "Hunyuan api key is missing. Please provide it in the config or set the HUNYUAN_API_KEY environment variable."
            )

        super().__init__('https://api.hunyuan.cloud.tencent.com/v1',
                         **current_config)
