import json
import os

import openai
from box import Box

from aisuite4cn.provider import Provider


class DeepseekProvider(Provider):
    """
    DeepSeek Provider
    """
    def __init__(self, **config):
        """
        Initialize the DeepSeek provider with the given configuration.
        Pass the entire configuration dictionary to the DeepSeek client constructor.
        """
        # Ensure API key is provided either in config or via environment variable

        self.config = dict(config)
        self.config.setdefault("api_key", os.getenv("DEEPSEEK_API_KEY"))
        if not self.config['api_key']:
            raise ValueError(
                "DeepSeek API key is missing. Please provide it in the config or set the DEEPSEEK_API_KEY environment variable."
            )
        # Pass the entire config to the DeepSeek client constructor
        self.client = openai.OpenAI(
            base_url = "https://api.deepseek.com/v1",
            **self.config)

    def chat_completions_create(self, model, messages, **kwargs):
        # Any exception raised by DeepSeek will be returned to the caller.
        # Maybe we should catch them and raise a custom LLMError.
        with_raw_response = model == "deepseek-reasoner"
        if with_raw_response:
            if not kwargs.get("stream", False):
                raw_response = self.client.with_raw_response.chat.completions.create(
                    model=model,
                    messages=messages,
                    **kwargs  # Pass any additional arguments to the DeepSeek API
                )
                return Box(json.loads(raw_response.text))
            else:
                response = self.client.with_streaming_response.chat.completions.create(
                    model=model,
                    messages=messages,
                    **kwargs  # Pass any additional arguments to the DeepSeek API
                )
                return self._create_for_stream(response)
        else:
            return self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs  # Pass any additional arguments to the DeepSeek API
            )

    def _create_for_stream(self, response):
        with response as raw_stream_response:
            # 使用 TextIOWrapper 包装字节流，并指定编码为 UTF-8
            for chunk in raw_stream_response.iter_bytes():

                # 逐行读取
                for line in chunk.decode('utf-8').split('\n'):
                    line = line.strip()  # 去除首尾空白字符（包括换行符）
                    if not line:
                        # 跳过空行
                        continue
                    if line.startswith('data: [DONE]'):
                        return
                    if line.startswith('data: '):
                        content = line[6:]
                        yield Box(json.loads(content))
