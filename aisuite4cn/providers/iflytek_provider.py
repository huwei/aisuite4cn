import os

from aisuite4cn.base_provider import BaseProvider


class IflytekProvider(BaseProvider):
    """
    iFlytek (讯飞星火) Provider，x2新版本
    Documentation: https://www.xfyun.cn/doc/spark/X1http.html#_1%E3%80%81%E8%AF%B7%E6%B1%82%E5%9C%B0%E5%9D%80
    """

    def __init__(self, **config):
        """
        Initialize the iFlytek provider with the given configuration.
        """
        current_config = dict(config)
        current_config.setdefault("api_key", os.getenv("IFLYTEK_API_KEY"))
        if not current_config.get("api_key"):
            raise ValueError(
                "iFlytek API key is missing. Please provide it in the config or set the IFLYTEK_API_KEY environment variable."
            )

        super().__init__("https://spark-api.xf-yun.com/x2", **current_config)

    def _prepare_chat_completions_call(self, model, messages, **kwargs):
        new_kwargs = dict(kwargs)
        new_kwargs.pop("frequency_penalty", None)
        new_kwargs.pop("presence_penalty", None)
        return model, messages, new_kwargs
