import openai
from aisuite4cn.provider import Provider

OPENAI_PARAMS = [
    "messages",
    "model",
    "audio",
    "response_format",
    "frequency_penalty",
    "function_call",
    "functions",
    "logit_bias",
    "logprobs",
    "max_completion_tokens",
    "max_tokens",
    "metadata",
    "modalities",
    "n",
    "parallel_tool_calls",
    "prediction",
    "presence_penalty",
    "prompt_cache_key",
    "reasoning_effort",
    "safety_identifier",
    "seed",
    "service_tier",
    "stop",
    "store",
    "stream",
    "stream_options",
    "temperature",
    "tool_choice",
    "tools",
    "top_logprobs",
    "top_p",
    "user",
    "verbosity"
]


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

    def _prepare_chat_completions_call(self, model, messages, **kwargs):
        return model, messages, kwargs

    def chat_completions_create(self, model, messages, **kwargs):
        """Create a chat completion using the OpenAI API."""
        model, messages, new_kwargs = self._prepare_chat_completions_call(model, messages, **kwargs)
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **self._compatible_with_openai_kwargs(new_kwargs)
        )



    async def async_chat_completions_create(self, model, messages, **kwargs):
        """Create a chat completion using the OpenAI API."""
        model, messages, new_kwargs = self._prepare_chat_completions_call(model, messages, **kwargs)
        return await self.async_client.chat.completions.create(
            model=model,
            messages=messages,
            **self._compatible_with_openai_kwargs(new_kwargs)
        )


    async def async_chat_completions_parse(self, model, messages, **kwargs):

        model, messages, new_kwargs = self._prepare_chat_completions_call(model, messages, **kwargs)
        return await self.async_client.chat.completions.parse(
            model=model,
            messages=messages,
            **self._compatible_with_openai_kwargs(new_kwargs)
        )

    def async_chat_completions_stream(self, model, messages, **kwargs):
        model, messages, new_kwargs = self._prepare_chat_completions_call(model, messages, **kwargs)
        return self.async_client.chat.completions.stream(
            model=model,
            messages=messages,
            **self._compatible_with_openai_kwargs(new_kwargs)
        )

    @staticmethod
    def _compatible_with_openai_kwargs(kwargs:dict=None) ->  dict:
        # add logic to convert kwargs to openai compatible kwargs
        new_kwargs = dict(kwargs) if kwargs else {}
        new_extra_body = dict(kwargs.get("extra_body", {}))
        for k, v in kwargs.items():
            if k not in OPENAI_PARAMS:
                new_extra_body[k] = new_kwargs.pop(k)
        if new_extra_body:
            new_kwargs["extra_body"] = new_extra_body
        return new_kwargs

