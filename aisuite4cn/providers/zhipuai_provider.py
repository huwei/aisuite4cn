import os

import openai
import zhipuai

from aisuite4cn.provider import Provider


class ZhipuaiProvider(Provider):
    """
    Zhipu Provider
    """

    def __init__(self, **config):
        """
        Initialize the Zhipu provider with the given configuration.
        Pass the entire configuration dictionary to the Zhipu client constructor.
        """
        # Ensure API key is provided either in config or via environment variable

        self.config = dict(config)
        self.config.setdefault("api_key", os.getenv("ZHIPUAI_API_KEY"))
        if not self.config["api_key"]:
            raise ValueError(
                "Zhipu API key is missing. Please provide it in the config or set the ZHIPUAI_API_KEY environment variable."
            )
        self._client = None
        self._async_client = None
        self.base_url = f"https://open.bigmodel.cn/api/paas/v4"

    @property
    def client(self):
        if self._client:
            self._client = zhipuai.ZhipuAI(**self.config)
        return self._client

    @property
    def async_client(self):
        """Getter for the OpenAI client."""
        if not self._async_client:
            self._async_client = openai.AsyncOpenAI(base_url=self.base_url, **self.config)
        return self._async_client

    def chat_completions_create(self, model, messages, **kwargs):
        # Any exception raised by Zhipu will be returned to the caller.
        # Maybe we should catch them and raise a custom LLMError.
        cpkwargs = dict(kwargs)
        # Note: Zhipu does not support the frequency_penalty and presence_penalty parameters.
        cpkwargs.pop('frequency_penalty', None)
        cpkwargs.pop('presence_penalty', None)
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **cpkwargs  # Pass any additional arguments to the Zhipu API
        )

    async def async_chat_completions_create(self, model, messages, **kwargs):
        cpkwargs = dict(kwargs)
        # Note: Zhipu does not support the frequency_penalty and presence_penalty parameters.
        cpkwargs.pop('frequency_penalty', None)
        cpkwargs.pop('presence_penalty', None)
        return await self.async_client.chat.completions.create(
            model=model,
            messages=messages,
            **cpkwargs  # Pass any additional arguments to the Zhipu API
        )
