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

    def chat_completions_create(self, model, messages, **kwargs):
        # Any exception raised by Zhipu will be returned to the caller.
        # Maybe we should catch them and raise a custom LLMError.
        new_kwargs = self._zhipuai_kwargs(kwargs)
        return super().chat_completions_create(model, messages, **new_kwargs)

    async def async_chat_completions_create(self, model, messages, **kwargs):
        new_kwargs = self._zhipuai_kwargs(kwargs)
        return await super().async_chat_completions_create(
            model=model,
            messages=messages,
            **new_kwargs  # Pass any additional arguments to the Zhipu API
        )


    async def async_chat_completions_parse(self, model, messages, **kwargs):
        new_kwargs = self._zhipuai_kwargs(kwargs)
        return await super().async_chat_completions_parse(model, messages, **new_kwargs)

    def async_chat_completions_stream(self, model, messages, **kwargs):
        new_kwargs = self._zhipuai_kwargs(kwargs)
        return super().async_chat_completions_stream(model, messages, **new_kwargs)

    @staticmethod
    def _zhipuai_kwargs(kwargs:dict):
        new_kwargs = dict(kwargs)
        # Note: Zhipu does not support the frequency_penalty and presence_penalty parameters.
        new_kwargs.pop('frequency_penalty')
        new_kwargs.pop('presence_penalty')
        return new_kwargs
