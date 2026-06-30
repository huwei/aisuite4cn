import os
import re

from aisuite4cn.providers.chat_responses_provider import ChatResponsesProvider


class ThinkTagStreamParser:
    """流式解析 <think></think> 标签的状态机。

    Ollama 的推理模型（如 deepseek-r1、qwen3 等）在 content 中
    使用 <think>...</think> 标签包裹思考内容，而非使用 OpenAI 标准的
    reasoning_content 字段。

    本解析器将 <think> 标签内的内容路由到 reasoning_content，
    标签外的内容路由到 content，支持标签跨 chunk 分割的情况。
    """

    THINK_OPEN = "<think>"
    THINK_CLOSE = "</think>"

    def __init__(self):
        self._in_think = False
        self._buffer = ""

    def feed(self, content):
        """Feed streaming content, yield (reasoning, content) tuples."""
        if not content:
            return

        self._buffer += content

        while self._buffer:
            if self._in_think:
                close_idx = self._buffer.find(self.THINK_CLOSE)
                if close_idx != -1:
                    reasoning = self._buffer[:close_idx]
                    self._buffer = self._buffer[close_idx + len(self.THINK_CLOSE):]
                    self._in_think = False
                    if reasoning:
                        yield reasoning, None
                else:
                    partial_start = self._find_partial_tag(self._buffer, self.THINK_CLOSE)
                    if partial_start > 0:
                        safe = self._buffer[:partial_start]
                        self._buffer = self._buffer[partial_start:]
                        if safe:
                            yield safe, None
                    elif partial_start == -1:
                        safe = self._buffer
                        self._buffer = ""
                        if safe:
                            yield safe, None
                    break
            else:
                open_idx = self._buffer.find(self.THINK_OPEN)
                if open_idx != -1:
                    content_before = self._buffer[:open_idx]
                    self._buffer = self._buffer[open_idx + len(self.THINK_OPEN):]
                    self._in_think = True
                    if content_before:
                        yield None, content_before
                else:
                    partial_start = self._find_partial_tag(self._buffer, self.THINK_OPEN)
                    if partial_start > 0:
                        safe = self._buffer[:partial_start]
                        self._buffer = self._buffer[partial_start:]
                        if safe:
                            yield None, safe
                    elif partial_start == -1:
                        safe = self._buffer
                        self._buffer = ""
                        if safe:
                            yield None, safe
                    break

    @staticmethod
    def _find_partial_tag(buffer, tag):
        """Find the longest partial tag match at end of buffer.

        Returns index where partial match starts, 0 if entire buffer is partial,
        or -1 if no partial match possible.
        """
        best = -1
        for i in range(1, min(len(tag), len(buffer) + 1)):
            if buffer.endswith(tag[:i]):
                best = len(buffer) - i
        return best

    def flush(self):
        """Flush remaining buffer. Call at end of stream."""
        if self._buffer:
            remaining = self._buffer
            self._buffer = ""
            if self._in_think:
                return remaining, None
            else:
                return None, remaining
        return None


def _parse_think_tags(content):
    """从非流式响应的 content 中提取 <think></think> 内容。

    Returns:
        (reasoning_content, content) 元组
    """
    if not content:
        return None, content

    match = re.search(r"<think>(.*?)</think>", content, re.DOTALL)

    if match:
        reasoning = match.group(1).strip()
        remaining = content[:match.start()] + content[match.end():]
        remaining = remaining.strip()
        return reasoning or None, remaining or None

    return None, content


def _build_chunk_from_result(chunk_template, reasoning, content, finish_reason=None):
    """根据解析结果构建新的 ChatCompletionChunk 或修改原 chunk。

    Args:
        chunk_template: 用作模板的原始 chunk（取 id/model/created 等字段）
        reasoning: reasoning_content 内容
        content: delta.content 内容
        finish_reason: finish_reason 值
    """
    new_delta = {}
    if chunk_template.choices and chunk_template.choices[0].delta.role:
        new_delta["role"] = chunk_template.choices[0].delta.role
    if reasoning:
        new_delta["reasoning_content"] = reasoning
    if content:
        new_delta["content"] = content

    chunk_dict = chunk_template.model_dump()
    chunk_dict["choices"] = [{
        "index": chunk_template.choices[0].index if chunk_template.choices else 0,
        "delta": new_delta,
        "finish_reason": finish_reason,
    }]
    return chunk_template.__class__.model_validate(chunk_dict)


def _process_chunk(chunk, parser):
    """处理流式 chunk，将 <think> 标签内容路由到 reasoning_content。

    Args:
        chunk: OpenAI ChatCompletionChunk
        parser: ThinkTagStreamParser 实例

    Yields:
        修改后的 ChatCompletionChunk 列表（一个输入 chunk 可能产生多个输出 chunk）
    """
    if not chunk.choices:
        yield chunk
        return

    delta = chunk.choices[0].delta
    content = delta.content

    if not content:
        yield chunk
        return

    results = list(parser.feed(content))

    if not results:
        # All content buffered for partial tag matching, skip this chunk
        return

    for reasoning, normal_content in results:
        if reasoning or normal_content:
            yield _build_chunk_from_result(
                chunk, reasoning, normal_content, chunk.choices[0].finish_reason
            )


class OllamaProvider(ChatResponsesProvider):
    """Ollama Provider

    支持推理模型（如 deepseek-r1、qwen3 等）的 <think></think> 标签处理：
    - 非流式：将 content 中的 <think>...</think> 内容提取到 reasoning_content
    - 流式：将 <think> 标签内的 chunk 路由到 delta.reasoning_content，
      标签外的 chunk 保留在 delta.content
    - 支持标签跨 chunk 分割的情况
    """

    def __init__(self, **config):
        current_config = dict(config)

        base_url = current_config.pop("base_url", os.getenv("OLLAMA_BASE_URL"))
        if not base_url:
            raise ValueError(
                "Ollama Base Url is missing. Please provide it in the config "
                "or set the OLLAMA_BASE_URL environment variable."
            )
        current_config["api_key"] = current_config.get(
            "api_key", os.getenv("OLLAMA_API_KEY", "ollama")
        )
        super().__init__(base_url, **current_config)

    @staticmethod
    def _process_non_streaming_response(response):
        """处理非流式响应，提取 <think> 内容到 reasoning_content。"""
        if not response.choices:
            return response

        message = response.choices[0].message
        content = message.content

        if not content or "<think>" not in content:
            return response

        reasoning, clean_content = _parse_think_tags(content)

        if reasoning is None:
            return response

        response_dict = response.model_dump()
        response_dict["choices"][0]["message"]["reasoning_content"] = reasoning
        response_dict["choices"][0]["message"]["content"] = clean_content

        return response.__class__.model_validate(response_dict)

    def chat_completions_create(self, model, messages, **kwargs):
        model, messages, new_kwargs = self._prepare_chat_completions_call(
            model, messages, **kwargs
        )

        is_stream = new_kwargs.get("stream", False)
        result = self.client.chat.completions.create(
            model=model,
            messages=messages,
            **self._compatible_with_openai_kwargs(new_kwargs),
        )

        if is_stream:
            return self._wrap_stream(result)
        return self._process_non_streaming_response(result)

    @staticmethod
    def _wrap_stream(stream):
        """包装流式响应，处理 <think> 标签。"""
        parser = ThinkTagStreamParser()
        last_chunk = None
        for chunk in stream:
            last_chunk = chunk
            yield from _process_chunk(chunk, parser)

        # Flush any remaining buffer at end of stream
        remaining = parser.flush()
        if remaining and last_chunk is not None:
            reasoning, normal_content = remaining
            if reasoning or normal_content:
                yield _build_chunk_from_result(last_chunk, reasoning, normal_content)  # type: ignore[arg-type]

    async def async_chat_completions_create(self, model, messages, **kwargs):
        model, messages, new_kwargs = self._prepare_chat_completions_call(
            model, messages, **kwargs
        )

        is_stream = new_kwargs.get("stream", False)
        result = await self.async_client.chat.completions.create(
            model=model,
            messages=messages,
            **self._compatible_with_openai_kwargs(new_kwargs),
        )

        if is_stream:
            return self._wrap_async_stream(result)
        return self._process_non_streaming_response(result)

    @staticmethod
    async def _wrap_async_stream(stream):
        """包装异步流式响应，处理 <think> 标签。"""
        parser = ThinkTagStreamParser()
        last_chunk = None
        async for chunk in stream:
            last_chunk = chunk
            for processed_chunk in _process_chunk(chunk, parser):
                yield processed_chunk

        # Flush any remaining buffer
        remaining = parser.flush()
        if remaining and last_chunk is not None:
            reasoning, normal_content = remaining
            if reasoning or normal_content:
                yield _build_chunk_from_result(last_chunk, reasoning, normal_content)  # type: ignore[arg-type]
