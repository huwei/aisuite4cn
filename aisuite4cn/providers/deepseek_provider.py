import json
import os
from copy import deepcopy

import openai
from box import Box
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

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
            base_url="https://api.deepseek.com/v1",
            **self.config)

    def chat_completions_create(self, model, messages, **kwargs):
        # Any exception raised by DeepSeek will be returned to the caller.
        # Maybe we should catch them and raise a custom LLMError.
        with_raw_response = model == "deepseek-reasoner"
        if with_raw_response:
            if not kwargs.get("stream", False):
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    **kwargs  # Pass any additional arguments to the DeepSeek API
                )
                if response.choices[0].message.reasoning_content:
                    if kwargs.get("response_format", None) and \
                        kwargs.get("response_format").get('type', None) == "json_object":
                        return response
                    else:
                        response.choices[0].message.content = (f'<think>' +
                                                               response.choices[0].message.reasoning_content +
                                                               '<\\think>\n' + response.choices[0].message.content)
                return response
            else:
                response = self.client.with_streaming_response.chat.completions.create(
                    model=model,
                    messages=messages,
                    **kwargs  # Pass any additional arguments to the DeepSeek API
                )
                return self._create_for_stream(response, **kwargs)
        else:
            return self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs  # Pass any additional arguments to the DeepSeek API
            )

    def _create_for_stream(self, response, **kwargs):
        """
        Create a generator for streaming DeepSeek responses.
        :param response: response
        :return: ChatCompletionChunk
        """
        has_think_counter = 0
        has_set_end = False
        with (response as raw_stream_response):
            for chunk in raw_stream_response.iter_lines():

                line = chunk.strip()  # 去除首尾空白字符（包括换行符）
                if not line:
                    # 跳过空行
                    continue
                if line.startswith('data: [DONE]'):
                    return
                if line.startswith('data: '):
                    content = line[6:]
                    json_dict = json.loads(content)
                    box = Box(json_dict)
                    chat_completion_chunk: ChatCompletionChunk = ChatCompletionChunk.model_validate(json_dict)

                    if box.choices[0].delta.reasoning_content:
                        has_think_counter += 1
                        if kwargs.get("response_format", None) and \
                                kwargs.get("response_format").get('type', None) == "json_object":
                            # 如果是json输出，请不需要输出思考
                            continue
                        if has_think_counter == 1:
                            chat_completion_chunk.choices[0].delta.content = '<think>'
                            yield chat_completion_chunk
                        chat_completion_chunk.choices[0].delta.content = box.choices[0].delta.reasoning_content
                        yield chat_completion_chunk
                    else:
                        # 已经结束
                        if has_think_counter >= 1 and not has_set_end:
                            has_set_end = True
                            if kwargs.get("response_format", None) and \
                                    kwargs.get("response_format").get('type', None) == "json_object":
                                # 如果是json输出，请不需要输出思考标记
                                pass
                            else:
                                think_end_chunk = deepcopy(chat_completion_chunk)
                                think_end_chunk.choices[0].delta.content = '<\\think>\n'
                                yield think_end_chunk

                        yield chat_completion_chunk
