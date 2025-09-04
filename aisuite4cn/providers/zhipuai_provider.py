import os

from aisuite4cn.provider import BaseProvider


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

    def chat_completions_create(self, model, messages, **kwargs):
        # Any exception raised by Zhipu will be returned to the caller.
        # Maybe we should catch them and raise a custom LLMError.
        cpkwargs = dict(kwargs)
        # Note: Zhipu does not support the frequency_penalty and presence_penalty parameters.
        cpkwargs.pop('frequency_penalty', None)
        cpkwargs.pop('presence_penalty', None)
        return super().chat_completions_create(model, messages, **cpkwargs)

    async def async_chat_completions_create(self, model, messages, **kwargs):
        cpkwargs = dict(kwargs)
        # Note: Zhipu does not support the frequency_penalty and presence_penalty parameters.
        cpkwargs.pop('frequency_penalty', None)
        cpkwargs.pop('presence_penalty', None)
        return await super().async_chat_completions_create(
            model=model,
            messages=messages,
            **cpkwargs  # Pass any additional arguments to the Zhipu API
        )
