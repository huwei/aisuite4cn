import os

from aisuite4cn.base_provider import BaseProvider


class StepfunProvider(BaseProvider):
    """
    Stepfun Provider
    """
    def __init__(self, **config):
        """
        Initialize the Stepfun provider with the given configuration.
        Pass the entire configuration dictionary to the Stepfun client constructor.
        """
        # Ensure API key (STEP_API_KEY) is provided either in config or via environment variable

        current_config = dict(config)
        current_config.setdefault("api_key", os.getenv("STEP_API_KEY"))
        if not current_config['api_key']:
            raise ValueError(
                "Stepfun API key is missing. Please provide it in the config or set the STEP_API_KEY environment variable."
            )

        super().__init__('https://api.stepfun.com/v1',
                         **current_config)

