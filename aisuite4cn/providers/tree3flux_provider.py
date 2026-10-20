import os

from aisuite4cn.chat_responses_provider import ChatResponsesProvider


class Tree3fluxProvider(ChatResponsesProvider):
    """
    Tree3flux Provider
    """

    def __init__(self, **config):
        """
        Initialize the Tree3flux provider with the given configuration.
        Pass the entire configuration dictionary to the Tree3flux client constructor.
        """
        # Ensure API key is provided either in config or via environment variable
        current_config = dict(config)
        current_config.setdefault("api_key", os.getenv("TREE3FLUX_API_KEY"))
        if not current_config['api_key']:
            raise ValueError(
                "Tree3flux API key is missing. Please provide it in the config or set the TREE3FLUX_API_KEY environment variable."
            )

        super().__init__('https://ai.zoomsys.com.cn/v1',
                         **current_config)
