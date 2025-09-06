import openai
from aisuite4cn.provider import Provider


class BaseProvider(Provider):
    """Base class for all openai compatible providers."""

    def __init__(self, base_url, **config):
        self.base_url = base_url
        self.config = dict(config)
        self._client = None
        self._async_client = None

    @property
    def client(self):
        """Getter for the OpenAI client."""
        if not self._client:
            self._client = openai.OpenAI(base_url=self.base_url, **self.config)
        return self._client

    @client.setter
    def client(self, value):
        """Setter for the OpenAI client."""
        self._client = value
    @property
    def async_client(self):
        """Getter for the asynchronous OpenAI client.

        Lazily initializes the AsyncOpenAI client if not already created.
        """
        if not self._async_client:
            self._async_client = openai.AsyncOpenAI(
                base_url=self.base_url,
                **self.config
            )
        return self._async_client

    @async_client.setter
    def async_client(self, value):
        """Setter for the asynchronous OpenAI client.

        Allows replacing the default client with a custom one.

        Args:
            value: An instance of openai.AsyncOpenAI or compatible client
        """
        self._async_client = value

    def chat_completions_create(self, model, messages, **kwargs):
        """Create a chat completion using the OpenAI API."""

        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )



    async def async_chat_completions_create(self, model, messages, **kwargs):
        """Create a chat completion using the OpenAI API."""
        return await self.async_client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )


    async def async_chat_completions_parse(self, model, messages, **kwargs):

        return await self.async_client.chat.completions.parse(
            model=model,
            messages=messages,
            **kwargs
        )

    def async_chat_completions_stream(self, model, messages, **kwargs):

        return self.async_client.chat.completions.stream(
            model=model,
            messages=messages,
            **kwargs
        )
