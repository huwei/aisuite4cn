import os
from xml.dom import NotSupportedErr

from volcenginesdkarkruntime import Ark, AsyncArk

from aisuite4cn.provider import Provider


class ArkProvider(Provider):
    """
    ByteDance Ark Provider
    """

    def __init__(self, **config):
        """
        Initialize the Volcengine provider with the given configuration.
        Pass the entire configuration dictionary to the Volcengine client constructor.
        """
        # Ensure API key is provided either in config or via environment variable
        self.config = dict(config)
        self.config.setdefault("api_key", os.getenv("ARK_API_KEY"))
        if not self.config["api_key"]:
            raise ValueError(
                "Ark API key is missing. Please provide it in the config or set the ARK_API_KEY environment variable."
            )
        # Pass the entire config to the Ark client constructor
        self._client = None
        self._async_client = None

    @property
    def client(self):
        """Getter for the OpenAI client."""
        if not self._client:
            self._client = Ark(**self.config)
        return self._client

    @property
    def async_client(self):
        """Getter for the OpenAI client."""
        if not self._async_client:
            self._async_client = AsyncArk(**self.config)
        return self._async_client

    def chat_completions_create(self, model, messages, **kwargs):

        # Any exception raised by Ark will be returned to the caller.
        # Maybe we should catch them and raise a custom LLMError.

        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs  # Pass any additional arguments to the Ark API
        )


    async def async_chat_completions_create(self, model, messages, **kwargs):

        return await self.async_client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs  # Pass any additional arguments to the Ark API
        )

    async def async_chat_completions_parse(self, model, messages, **kwargs):
        raise NotImplementedError


    def async_chat_completions_stream(self, model, messages, **kwargs):
        raise NotImplementedError