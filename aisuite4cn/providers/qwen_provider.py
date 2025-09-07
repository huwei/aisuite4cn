import os

from aisuite4cn.base_provider import BaseProvider


class QwenProvider(BaseProvider):
    """
    Aliyun Qwen Provider
    """

    def __init__(self, **config):
        """
        Initialize the Qwen shot provider with the given configuration.
        Pass the entire configuration dictionary to the Qwen client constructor.
        """
        # Ensure API key is provided either in config or via environment variable
        current_config = dict(config)
        current_config.setdefault("api_key", os.getenv("DASHSCOPE_API_KEY"))
        if not current_config['api_key']:
            raise ValueError(
                "Dashscope API key is missing. Please provide it in the config or set the DASHSCOPE_API_KEY environment variable."
            )
        super().__init__('https://dashscope.aliyuncs.com/compatible-mode/v1',
                         **current_config)
