from abc import ABC

from .provider import ProviderFactory


class Client:
    def __init__(self, provider_configs=None):
        """
        Initialize the client with provider configurations.
        Use the ProviderFactory to create provider instances.

        Args:
            provider_configs (dict): A dictionary containing provider configurations.
                Each key should be a provider string (e.g., "google" or "aws-bedrock"),
                and the value should be a dictionary of configuration options for that provider.
                For example:
                {
                    "openai": {"api_key": "your_openai_api_key"},
                    "aws-bedrock": {
                        "aws_access_key": "your_aws_access_key",
                        "aws_secret_key": "your_aws_secret_key",
                        "aws_region": "us-west-2"
                    }
                }
        """
        if provider_configs is None:
            provider_configs = {}
        self.providers = {}
        self.provider_configs = provider_configs
        self._chat = None
        self._initialize_providers()

    def _initialize_providers(self):
        """Helper method to initialize or update providers."""
        for provider_key, config in self.provider_configs.items():
            provider_key = self._validate_provider_key(provider_key)
            self.providers[provider_key] = ProviderFactory.create_provider(
                provider_key, config
            )

    def _validate_provider_key(self, provider_key):
        """
        Validate if the provider key corresponds to a supported provider.
        """
        supported_providers = ProviderFactory.get_supported_providers()

        if provider_key not in supported_providers:
            raise ValueError(
                f"Invalid provider key '{provider_key}'. Supported providers: {supported_providers}. "
                "Make sure the model string is formatted correctly as 'provider:model'."
            )

        return provider_key

    def configure(self, provider_configs: dict = None):
        """
        Configure the client with provider configurations.
        """
        if provider_configs is None:
            return

        self.provider_configs.update(provider_configs)
        self._initialize_providers()  # NOTE: This will override existing provider instances.

    @property
    def chat(self):
        """Return the chat API interface."""
        if not self._chat:
            self._chat = Chat(self)
        return self._chat


class AsyncClient(Client):

    @property
    def chat(self):
        """Return the chat API interface."""
        if not self._chat:
            self._chat = AsyncChat(self)
        return self._chat


class Chat:
    def __init__(self, client: "Client"):
        self.client = client
        self._completions = Completions(self.client)

    @property
    def completions(self):
        """Return the completions interface."""
        return self._completions


class AsyncChat:
    def __init__(self, client: "AsyncClient"):
        self.client = client
        self._completions = AsyncCompletions(self.client)

    @property
    def completions(self):
        """Return the completions interface."""
        return self._completions


class BaseCompletions(ABC):

    def __init__(self, client):
        self.client = client

    @staticmethod
    def _get_provider_key_and_model_name(model):
        """
        Extract the provider key and model name from the model string.
        """
        if ":" not in model:
            raise ValueError(
                f"Invalid model format. Expected 'provider:model', got '{model}'"
            )
        # Find the first ':' to split provider_key and model_name
        separator_index = model.find(':')
        if separator_index == -1:
            raise ValueError("Model identifier must contain a ':' to specify the provider key and model name.")
        model_name = model[separator_index + 1:]
        provider_key = model[:separator_index]
        return provider_key, model_name

    def _get_provider(self, provider_key):
        # Validate if the provider is supported
        supported_providers = ProviderFactory.get_supported_providers()
        if provider_key not in supported_providers:
            raise ValueError(
                f"Invalid provider key '{provider_key}'. Supported providers: {supported_providers}. "
                "Make sure the model string is formatted correctly as 'provider:model'."
            )
        # Initialize provider if not already initialized
        if provider_key not in self.client.providers:
            config = self.client.provider_configs.get(provider_key, {})
            self.client.providers[provider_key] = ProviderFactory.create_provider(
                provider_key, config
            )
        provider = self.client.providers.get(provider_key)
        if not provider:
            raise ValueError(f"Could not load provider for '{provider_key}'.")
        return provider


class AsyncCompletions(BaseCompletions):

    def __init__(self, client: "AsyncClient"):
        super().__init__(client)

    async def create(self, model: str, messages: list, **kwargs):
        """
        Create chat completion based on the model, messages, and any extra arguments.
        """
        # Check that correct format is used
        provider_key, model_name = self._get_provider_key_and_model_name(model)

        provider = self._get_provider(provider_key)

        # Delegate the chat completion to the correct provider's implementation
        return await provider.async_chat_completions_create(model_name, messages, **kwargs)


    async def parse(self, model, messages, **kwargs):
        """
        Parse chat completion based on the model, messages, and any extra arguments.
        """
        # Check that correct format is used
        provider_key, model_name = self._get_provider_key_and_model_name(model)

        provider = self._get_provider(provider_key)

        # Delegate the chat completion to the correct provider's implementation
        return await provider.async_chat_completions_parse(model_name, messages, **kwargs)

    def async_chat_completions_stream(self, model, messages, **kwargs):
        """
        Stream chat completion based on the model, messages, and any extra arguments.
        """
        # Check that correct format is used
        provider_key, model_name = self._get_provider_key_and_model_name(model)

        provider = self._get_provider(provider_key)

        # Delegate the chat completion to the correct provider's implementation
        return provider.async_chat_completions_stream(model_name, messages, **kwargs)


class Completions(BaseCompletions):

    def __init__(self, client: "Client"):
        super().__init__(client)

    def create(self, model: str, messages: list, **kwargs):
        """
        Create chat completion based on the model, messages, and any extra arguments.
        """
        # Check that correct format is used
        provider_key, model_name = self._get_provider_key_and_model_name(model)

        provider = self._get_provider(provider_key)

        # Delegate the chat completion to the correct provider's implementation
        return provider.chat_completions_create(model_name, messages, **kwargs)
