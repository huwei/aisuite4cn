import os

from aisuite4cn.base_provider import BaseProvider


class ZhipuaiProvider(BaseProvider):
    """
    Zhipu Provider
    """

    def __init__(self, **config):
        """
        Initialize the Zhipu provider with the given configuration.
        Pass the entire configuration dictionary to the Zhipu client constructor.
        """
        # Ensure API key is provided either in config or via environment variable

        current_config = dict(config)
        current_config.setdefault("api_key", os.getenv("ZHIPUAI_API_KEY"))
        if not current_config["api_key"]:
            raise ValueError(
                "Zhipu API key is missing. Please provide it in the config or set the ZHIPUAI_API_KEY environment variable."
            )

        super().__init__('https://open.bigmodel.cn/api/paas/v4',
                         **current_config)

    def _prepare_chat_completions_call(self, model, messages, **kwargs):
        new_kwargs = dict(kwargs)
        # Note: Zhipu does not support the frequency_penalty and presence_penalty parameters.
        new_kwargs.pop('frequency_penalty', None)
        new_kwargs.pop('presence_penalty', None)
        return model, messages, new_kwargs

