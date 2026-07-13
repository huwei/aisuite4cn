import json
import os
from typing import Iterator, AsyncIterator

import openai
from future.backports import datetime
from openai._streaming import SSEDecoder, ServerSentEvent

from aisuite4cn.base_provider import BaseProvider


class HermesSSEDecoder:
    """将 hermes 自定义 SSE 事件转换为 OpenAI 标准 tool_calls 格式的解码器。

    hermes-agent 服务端在执行工具时，会在 SSE 流中发送
    event: hermes.tool.progress 类型的自定义事件，其 data 格式为：
    {"tool": "skill_view|terminal", "status": "running|completed",
     "toolCallId": "call_00_xxx", "label": "...", "emoji": "..."}

    这些事件不是标准 OpenAI chat completion chunk 格式，
    直接传给 OpenAI SDK 会导致 pydantic 验证错误。

    本解码器将这些 hermes 事件转换为 OpenAI 标准的 tool_calls 流式格式：
    - status="running" → 生成 ChatCompletionChunk，delta 中包含 tool_calls
    - status="completed" → 跳过（OpenAI 标准格式中无对应概念）

    转换后的格式示例：
    {
      "id": "chatcmpl-xxx",
      "object": "chat.completion.chunk",
      "choices": [{
        "delta": {
          "tool_calls": [{
            "index": 0,
            "id": "call_00_xxx",
            "type": "function",
            "function": {
              "name": "terminal",
              "arguments": "{\\"command\\": \\"python scripts/...\\u0022}"
            }
          }]
        },
        "finish_reason": null
      }]
    }

    注意：hermes-agent 的工具在服务端自主执行，不需要客户端回传工具结果。
    转换后的 tool_calls 仅供客户端感知工具调用进度，客户端不需要执行这些工具。
    """
    STATUS_MAP = {
        "running": "in_progress",
        "completed": "completed",
    }

    def __init__(self):
        self._decoder = SSEDecoder()
        self._tool_call_index = -1
        # 从标准 OpenAI chunk 中提取上下文信息，用于构建转换后的 chunk
        self._chat_id = "chatcmpl-hermes"
        self._created = 0
        self._model = "hermes-agent"
        self._tool_call_ids = {}
        self._tool_call_buffer: dict = {}
        self._tool_call_id = None

    def _convert_hermes_tool_progress(self, event_data: dict) -> ServerSentEvent | None:
        """将 hermes.tool.progress 事件转换为 OpenAI 标准 tool_calls 格式的 SSE 事件。

        Args:
            event_data: hermes.tool.progress 事件的 JSON 数据

        Returns:
            转换后的 ServerSentEvent，如果不需要转换则返回 None
        """
        status = HermesSSEDecoder.STATUS_MAP.get(event_data.get("status", 'running'), "in_progress")

        tool_call_id = event_data["toolCallId"]

        chunk_data = {
            "id": self._chat_id,
            "object": "chat.completion.chunk",
            "created": self._created,
            "model": self._model,
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "tool_calls": [
                            {
                                "index": 0,
                                "id": tool_call_id,
                                "type": "function",
                                "function": {
                                    "name": '',
                                    "arguments": '',
                                },
                                "status": "in_progress"
                            }
                        ]
                    },
                    "finish_reason": None,
                }
            ],
        }
        is_new = False
        if tool_call_id not in self._tool_call_buffer:
            self._tool_call_index += 1
            is_new = True

        tool_call = self._tool_call_buffer.setdefault(
            tool_call_id, chunk_data
        )
        # 10 位 时间戳
        self._created = int(datetime.datetime.now().timestamp())
        tool_call["created"] = self._created
        label = event_data.get("label", "")

        # 根据 hermes 工具类型构建不同的 arguments
        tool = event_data.get("tool", "unknown")
        if tool == "terminal":
            arguments = json.dumps({"command": label})
        else:
            # skill_view 等其他工具类型
            arguments = json.dumps({"label": label}) if label else "{}"

        if is_new:
            emoji = event_data.get("emoji", "")
            tool_name = f"{emoji} {tool}".strip()
            tool_call["choices"][0]["delta"]["tool_calls"][0]["function"]["name"] = tool_name
            tool_call["choices"][0]["delta"]["tool_calls"][0]["index"] = self._tool_call_index
            tool_call["choices"][0]["delta"]["tool_calls"][0]["function"]["arguments"] = arguments
        # status是非标准字段
        tool_call["choices"][0]["delta"]["tool_calls"][0]["status"] = status

        self._tool_call_id = tool_call_id

        return ServerSentEvent(data=json.dumps(tool_call))

    def _update_chat_context(self, event: ServerSentEvent):
        """从标准 OpenAI 事件中提取 chat id、model 等上下文信息。

        这些信息用于构建转换后的 hermes 事件对应的 ChatCompletionChunk。
        """
        try:
            data = json.loads(event.data)
            if data.get("id"):
                self._chat_id = data["id"]
            if data.get("created"):
                self._created = data["created"]
            if data.get("model"):
                self._model = data["model"]
        except (json.JSONDecodeError, TypeError):
            pass

    def _process_hermes_event(self, event: ServerSentEvent) -> ServerSentEvent | None:
        """处理 hermes.* 事件：解析 JSON 并转换为 OpenAI 标准格式。

        Returns:
            转换后的 ServerSentEvent，解析失败则返回 None
        """
        try:
            data = json.loads(event.data)
            return self._convert_hermes_tool_progress(data)
        except (json.JSONDecodeError, TypeError):
            return None

    def iter_bytes(self, iterator: Iterator[bytes]) -> Iterator[ServerSentEvent]:
        for event in self._decoder.iter_bytes(iterator):
            self._update_chat_context(event)
            if event.event and event.event.startswith("hermes."):
                converted = self._process_hermes_event(event)
                if converted:
                    yield converted
            else:
                yield event

    async def aiter_bytes(self, iterator: AsyncIterator[bytes]) -> AsyncIterator[ServerSentEvent]:
        async for event in self._decoder.aiter_bytes(iterator):
            self._update_chat_context(event)
            if event.event and event.event.startswith("hermes."):
                converted = self._process_hermes_event(event)
                if converted:
                    yield converted
            else:
                yield event


class HermesOpenAI(openai.OpenAI):
    """自定义 OpenAI 客户端，注入 HermesSSEDecoder 以转换 hermes SSE 事件为标准 tool_calls 格式。"""

    def _make_sse_decoder(self):
        return HermesSSEDecoder()


class HermesAsyncOpenAI(openai.AsyncOpenAI):
    """自定义异步 OpenAI 客户端，注入 HermesSSEDecoder 以转换 hermes SSE 事件为标准 tool_calls 格式。"""

    def _make_sse_decoder(self):
        return HermesSSEDecoder()


class HermesAgentProvider(BaseProvider):
    """Hermes Agent Provider

    hermes-agent 是一个服务端自主执行工具的 AI 代理服务，
    暴露 OpenAI 兼容的 /v1/chat/completions 端点。

    核心特点：
    - 工具在服务端执行，客户端不需要回传工具结果
    - SSE 流中会发送 event: hermes.tool.progress 事件通知工具执行进度
    - 通过自定义 SSE 解码器将这些事件转换为 OpenAI 标准 tool_calls 格式

    转换后的流式输出序列示例：
    1. {"delta": {"role": "assistant"}}              — 角色
    2. {"delta": {"tool_calls": [...]}}              — 工具调用（由 hermes.tool.progress 转换）
    3. {"delta": {"content": "..."}}                 — 最终文本回答
    4. {"delta": {}, "finish_reason": "stop"}        — 结束

    注意：转换后的 tool_calls 仅供客户端感知工具调用进度，
    客户端不需要执行这些工具或回传工具结果。

    配置方式：
    - HERMES_AGENT_API_KEY: API 密钥（内网部署可留空）
    - HERMES_AGENT_BASE_URL: 服务地址（默认 http://localhost:18642/v1）
    """

    def __init__(self, **config):
        current_config = dict(config)
        current_config.setdefault(
            "api_key", os.getenv("HERMES_AGENT_API_KEY", None)
        )
        base_url = current_config.pop(
            "base_url",
            os.getenv("HERMES_AGENT_BASE_URL", None),
        )
        if not base_url:
            raise ValueError(
                "Hermes Agent Base URL is missing. Please provide it in the config "
                "or set the HERMES_AGENT_BASE_URL environment variable."
            )
        super().__init__(base_url, **current_config)

    @property
    def client(self):
        if not self._client:
            self._client = HermesOpenAI(base_url=self.base_url, **self.config)
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    @property
    def async_client(self):
        if not self._async_client:
            self._async_client = HermesAsyncOpenAI(
                base_url=self.base_url, **self.config
            )
        return self._async_client

    @async_client.setter
    def async_client(self, value):
        self._async_client = value
