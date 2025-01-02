from urllib.parse import parse_qs

import openai
import os
from aisuite4cn.provider import Provider, LLMError


class SparkProvider(Provider):
    """
    Moonshot Provider
    """
    def __init__(self, **config):
        """
        Initialize the Spark provider with the given configuration.
        Pass the entire configuration dictionary to the Spark client constructor.
        api_key_map Example:
        {
            "api_key_map": {
                # Key is the model name, and value is the corresponding API password.
                # This mapping allows you to specify different API passwords for different models.
                # Example:
                "4.0Ultra":"your-4.0Ultra-APIPassword", # API password for the 4.0Ultra model
                "generalv3":"your-generalv3-APIPassword" # API password for the generalv3 model
            }
        }
        """
        # Ensure API key is provided either in config or via environment variable

        self.config = dict(config)
        env_api_key_map = {k: v[0] for k, v in parse_qs(os.getenv("SPARK_API_KEY_MAP", "")).items()}
        self.api_key_map=self.config.pop("api_key_map", env_api_key_map)
        self.client = openai.OpenAI(
            api_key="default",
            base_url = "https://spark-api-open.xf-yun.com/v1",
            **self.config)

    def chat_completions_create(self, model, messages, **kwargs):
        # Any exception raised by Moonshot will be returned to the caller.
        # Maybe we should catch them and raise a custom LLMError.
        if not self.api_key_map[model]:
            raise ValueError(
                "Spark API key is missing. Please provide it in the config or set the SPARK_API_KEY_MAP environment variable."
            )
        self.client.api_key = self.api_key_map[model]
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs  # Pass any additional arguments to the Moonshot API
        )

