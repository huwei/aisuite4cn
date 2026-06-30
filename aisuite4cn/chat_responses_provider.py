"""
Chat-to-Responses fallback provider.

This module provides :class:`ChatResponsesProvider`, a :class:`BaseProvider`
subclass that bridges the OpenAI Responses API protocol to the Chat Completions
API for providers whose servers do not yet expose a native ``/v1/responses``
endpoint.

All responses_* methods (sync, async, streaming) are implemented by converting
the request to a chat-completions call and converting the result back to the
responses API shape defined by ``openai.types.responses``.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Union

from openai import AsyncStream, Stream
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_chunk import (
    ChatCompletionChunk,
    Choice as ChunkChoice,
    ChoiceDelta as ChunkChoiceDelta,
)
from openai.types.completion_usage import CompletionUsage
from openai.types.responses import (
    Response,
    ResponseCompletedEvent,
    ResponseContentPartAddedEvent,
    ResponseCreatedEvent,
    ResponseInProgressEvent,
    ResponseOutputItemAddedEvent,
    ResponseOutputItemDoneEvent,
    ResponseOutputMessage,
    ResponseOutputText,
    ResponseStreamEvent,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
    ResponseUsage,
)
from openai.types.responses.response_output_text import AnnotationFileCitation
from openai.types.responses.response_usage import (
    InputTokensDetails,
    OutputTokensDetails,
)

from aisuite4cn.base_provider import BaseProvider

# ---------------------------------------------------------------------------
# Input conversion helpers
# ---------------------------------------------------------------------------

# Recognised roles for easy-input messages that carry a "role" key.
_CHAT_ROLES = frozenset({"user", "system", "assistant", "developer", "tool"})


def _is_content_list(value: Any) -> bool:
    """Return *True* if *value* looks like a list of content parts.

    OpenAIʼs Responses API accepts ``input`` as either a plain string or a
    list.  Each list element may be a ``{"role": "...", "content": ...}``
    easy-input message or a typed item object (``{"type": "message", ...}``).
    """
    return isinstance(value, list)


def _normalise_text_content(content: Any) -> Union[str, List[Dict[str, Any]]]:
    """Convert a Responses content payload to Chat-Completions content.

    Handles:
    * plain string
    * list of ``{"type": "input_text", "text": "..."}`` dicts
    * list of ``{"type": "input_image", ...}`` dicts (passed through)
    * anything else (returned as-is)
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[Dict[str, Any]] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "input_text":
                parts.append({"type": "text", "text": item.get("text", "")})
            elif isinstance(item, dict):
                parts.append(item)
            else:
                parts.append({"type": "text", "text": str(item)})
        return parts
    return content


def responses_input_to_messages(
    input_value: Union[str, List[Dict[str, Any]]],
    instructions: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Convert a Responses-API *input* value into a Chat-Completions
    ``messages`` list.

    Parameters
    ----------
    input_value:
        The ``input`` field from a Responses request — either a plain string
        (treated as a single user message) or a list of easy-input messages /
        typed items.
    instructions:
        Optional top-level ``instructions`` string.  When present, it is
        prepended as a ``system``-role message.

    Returns
    -------
    list[dict]
        ``messages`` list ready for the Chat Completions endpoint.
    """
    messages: List[Dict[str, Any]] = []

    if instructions:
        messages.append({"role": "system", "content": str(instructions)})

    if not input_value:
        return messages

    if isinstance(input_value, str):
        messages.append({"role": "user", "content": input_value})
        return messages

    # input_value is a list — iterate over items
    for item in input_value:
        if not isinstance(item, dict):
            messages.append({"role": "user", "content": str(item)})
            continue

        # Easy-input message: {"role": "...", "content": "..."}
        role = item.get("role")
        if role in _CHAT_ROLES:
            content = _normalise_text_content(item.get("content", ""))
            role_str: str = role  # type narrowing
            msg: Dict[str, Any] = {"role": role_str, "content": content}
            # Carry forward name if present (for tool / function messages)
            if "name" in item:
                msg["name"] = item["name"]
            if "tool_call_id" in item:
                msg["tool_call_id"] = item["tool_call_id"]
            if "tool_calls" in item:
                msg["tool_calls"] = item["tool_calls"]
            messages.append(msg)
            continue

        # Typed item: {"type": "message", "role": "...", "content": [...]}
        item_type = item.get("type", "")
        if item_type == "message":
            item_role = item.get("role", "user")
            item_content = _normalise_text_content(item.get("content", ""))
            messages.append({"role": item_role, "content": item_content})
        else:
            # Fallback: treat unknown typed items as user content
            messages.append({"role": "user", "content": str(item)})

    # Ensure there is at least one user message if the list is empty after
    # filtering (defensive).
    if not messages:
        messages.append({"role": "user", "content": str(input_value)})

    return messages


# ---------------------------------------------------------------------------
# Output conversion helpers
# ---------------------------------------------------------------------------


def _generate_id(prefix: str = "") -> str:
    """Generate a unique id string, optionally prefixed."""
    return prefix + uuid.uuid4().hex[:24]


def chat_completion_to_response(
    chat_response: ChatCompletion,
    *,
    response_id: Optional[str] = None,
) -> Response:
    """Convert a Chat-Completion response into an OpenAI Responses
    :class:`Response` object.

    Parameters
    ----------
    chat_response:
        The synchronous ChatCompletion returned by the provider.
    response_id:
        Optional override for the top-level response ``id``.  When *None*,
        a new ``resp_<uuid>`` id is generated.

    Returns
    -------
    Response
        A fully-populated Responses API response object.
    """
    if response_id is None:
        response_id = _generate_id("resp_")

    choice: Choice = chat_response.choices[0] if chat_response.choices else Choice(
        finish_reason="stop",
        index=0,
        message={"role": "assistant", "content": ""},  # type: ignore[arg-type]
    )

    message = choice.message
    content_text: str = message.content or ""

    msg_id = _generate_id("msg_")
    output_item = ResponseOutputMessage(
        id=msg_id,
        type="message",
        role="assistant",
        status="completed",
        content=[
            ResponseOutputText(
                type="output_text",
                text=content_text,
                annotations=[],
            )
        ],
    )

    usage: Optional[CompletionUsage] = chat_response.usage
    response_usage: Optional[ResponseUsage] = None
    if usage is not None:
        response_usage = ResponseUsage(
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            input_tokens_details=InputTokensDetails(cached_tokens=0),
            output_tokens_details=OutputTokensDetails(reasoning_tokens=0),
        )

    return Response(
        id=response_id,
        created_at=float(chat_response.created),
        model=chat_response.model,
        object="response",
        output=[output_item],
        parallel_tool_calls=True,
        tool_choice="auto",
        tools=[],
        status="completed",
        usage=response_usage,
    )


# ---------------------------------------------------------------------------
# Streaming conversion
# ---------------------------------------------------------------------------

# Mapping from Responses-API param name → Chat-Completions param name for
# parameters that exist in both APIs.
_RESPONSES_TO_CHAT_PARAM_MAP: Dict[str, str] = {
    "temperature": "temperature",
    "top_p": "top_p",
    "max_output_tokens": "max_tokens",
    "stop": "stop",
    "stream": "stream",
    "user": "user",
    "metadata": "metadata",
    "store": "store",
    "service_tier": "service_tier",
    "parallel_tool_calls": "parallel_tool_calls",
    "top_logprobs": "top_logprobs",
}

# Names of parameters that are Responses-API‑specific and must be dropped
# rather than passed through to Chat Completions.
_RESPONSES_ONLY_PARAMS = frozenset({
    "input",
    "instructions",
    "background",
    "context_management",
    "conversation",
    "include",
    "max_tool_calls",
    "moderation",
    "previous_response_id",
    "prompt",
    "prompt_cache_key",
    "prompt_cache_retention",
    "reasoning",
    "safety_identifier",
    "text",
    "truncation",
    "tool_choice",
    "tools",
    "stream_options",
})


def _map_responses_kwargs_to_chat(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Extract Chat-Completions-compatible kwargs from Responses kwargs.

    Parameters that exist in both APIs (e.g. *temperature*, *top_p*) are
    renamed where necessary.  Responses-only parameters are dropped.
    Unknown parameters are preserved in ``extra_body`` for providers that
    accept additional fields.
    """
    chat_kwargs: Dict[str, Any] = {}
    extra_body: Dict[str, Any] = {}

    for key, value in kwargs.items():
        if key in _RESPONSES_ONLY_PARAMS:
            continue
        mapped = _RESPONSES_TO_CHAT_PARAM_MAP.get(key)
        if mapped is not None:
            chat_kwargs[mapped] = value
        elif key in ("extra_headers", "extra_query", "extra_body"):
            chat_kwargs[key] = value
        else:
            extra_body[key] = value

    if extra_body:
        existing_extra = chat_kwargs.get("extra_body", {})
        if isinstance(existing_extra, dict):
            existing_extra.update(extra_body)
            chat_kwargs["extra_body"] = existing_extra
        else:
            chat_kwargs["extra_body"] = extra_body

    return chat_kwargs


def _build_stream_events(
    stream: Stream[ChatCompletionChunk],
    response_id: str,
    msg_id: str,
    model: str,
) -> Iterator[ResponseStreamEvent]:
    """Wrap a synchronous ChatCompletions *stream* into Responses stream events.

    Yields the canonical event sequence:
    ``response.created → response.in_progress → response.output_item.added →
    response.content_part.added → N × response.output_text.delta →
    response.output_text.done → response.output_item.done →
    response.completed``
    """
    created_at = float(int(time.time()))

    # -- response.created ---------------------------------------------------
    empty_resp = Response(
        id=response_id,
        created_at=created_at,
        model=model,
        object="response",
        output=[],
        parallel_tool_calls=True,
        tool_choice="auto",
        tools=[],
        status="in_progress",
    )
    yield ResponseCreatedEvent(
        type="response.created",
        sequence_number=0,
        response=empty_resp,
    )

    # -- response.in_progress -----------------------------------------------
    yield ResponseInProgressEvent(
        type="response.in_progress",
        sequence_number=1,
        response=empty_resp,
    )

    # -- response.output_item.added -----------------------------------------
    output_msg = ResponseOutputMessage(
        id=msg_id,
        type="message",
        role="assistant",
        status="in_progress",
        content=[],
    )
    yield ResponseOutputItemAddedEvent(
        type="response.output_item.added",
        sequence_number=2,
        output_index=0,
        item=output_msg,
    )

    # -- response.content_part.added ----------------------------------------
    content_part = ResponseOutputText(
        type="output_text",
        text="",
        annotations=[],
    )
    yield ResponseContentPartAddedEvent(
        type="response.content_part.added",
        sequence_number=3,
        item_id=msg_id,
        output_index=0,
        content_index=0,
        part=content_part,
    )

    # -- Walk the chat stream -----------------------------------------------
    seq = 4
    full_text = ""
    final_usage: Optional[CompletionUsage] = None

    for chunk in stream:
        if not chunk.choices:
            # Update usage from the chunk if present
            if chunk.usage is not None:
                final_usage = chunk.usage
            continue

        delta: ChunkChoiceDelta = chunk.choices[0].delta
        content_delta = delta.content

        if content_delta:
            full_text += content_delta
            yield ResponseTextDeltaEvent(
                type="response.output_text.delta",
                sequence_number=seq,
                item_id=msg_id,
                output_index=0,
                content_index=0,
                delta=content_delta,
                logprobs=[],
            )
            seq += 1

        # Capture usage from any chunk that carries it
        if chunk.usage is not None:
            final_usage = chunk.usage

    # -- response.output_text.done ------------------------------------------
    yield ResponseTextDoneEvent(
        type="response.output_text.done",
        sequence_number=seq,
        item_id=msg_id,
        output_index=0,
        content_index=0,
        text=full_text,
        logprobs=[],
    )
    seq += 1

    # -- response.output_item.done ------------------------------------------
    completed_msg = ResponseOutputMessage(
        id=msg_id,
        type="message",
        role="assistant",
        status="completed",
        content=[
            ResponseOutputText(
                type="output_text",
                text=full_text,
                annotations=[],
            )
        ],
    )
    yield ResponseOutputItemDoneEvent(
        type="response.output_item.done",
        sequence_number=seq,
        output_index=0,
        item=completed_msg,
    )
    seq += 1

    # -- response.completed -------------------------------------------------
    resp_usage: Optional[ResponseUsage] = None
    if final_usage is not None:
        resp_usage = ResponseUsage(
            input_tokens=final_usage.prompt_tokens,
            output_tokens=final_usage.completion_tokens,
            total_tokens=final_usage.total_tokens,
            input_tokens_details=InputTokensDetails(cached_tokens=0),
            output_tokens_details=OutputTokensDetails(reasoning_tokens=0),
        )

    completed_resp = Response(
        id=response_id,
        created_at=created_at,
        model=model,
        object="response",
        output=[completed_msg],
        parallel_tool_calls=True,
        tool_choice="auto",
        tools=[],
        status="completed",
        usage=resp_usage,
    )
    yield ResponseCompletedEvent(
        type="response.completed",
        sequence_number=seq,
        response=completed_resp,
    )


async def _build_async_stream_events(
    stream: AsyncStream[ChatCompletionChunk],
    response_id: str,
    msg_id: str,
    model: str,
) -> AsyncIterator[ResponseStreamEvent]:
    """Async variant of :func:`_build_stream_events`."""
    created_at = float(int(time.time()))

    # -- response.created ---------------------------------------------------
    empty_resp = Response(
        id=response_id,
        created_at=created_at,
        model=model,
        object="response",
        output=[],
        parallel_tool_calls=True,
        tool_choice="auto",
        tools=[],
        status="in_progress",
    )
    yield ResponseCreatedEvent(
        type="response.created",
        sequence_number=0,
        response=empty_resp,
    )

    # -- response.in_progress -----------------------------------------------
    yield ResponseInProgressEvent(
        type="response.in_progress",
        sequence_number=1,
        response=empty_resp,
    )

    # -- response.output_item.added -----------------------------------------
    output_msg = ResponseOutputMessage(
        id=msg_id,
        type="message",
        role="assistant",
        status="in_progress",
        content=[],
    )
    yield ResponseOutputItemAddedEvent(
        type="response.output_item.added",
        sequence_number=2,
        output_index=0,
        item=output_msg,
    )

    # -- response.content_part.added ----------------------------------------
    content_part = ResponseOutputText(
        type="output_text",
        text="",
        annotations=[],
    )
    yield ResponseContentPartAddedEvent(
        type="response.content_part.added",
        sequence_number=3,
        item_id=msg_id,
        output_index=0,
        content_index=0,
        part=content_part,
    )

    # -- Walk the chat stream -----------------------------------------------
    seq = 4
    full_text = ""
    final_usage: Optional[CompletionUsage] = None

    async for chunk in stream:
        if not chunk.choices:
            if chunk.usage is not None:
                final_usage = chunk.usage
            continue

        delta: ChunkChoiceDelta = chunk.choices[0].delta
        content_delta = delta.content

        if content_delta:
            full_text += content_delta
            yield ResponseTextDeltaEvent(
                type="response.output_text.delta",
                sequence_number=seq,
                item_id=msg_id,
                output_index=0,
                content_index=0,
                delta=content_delta,
                logprobs=[],
            )
            seq += 1

        if chunk.usage is not None:
            final_usage = chunk.usage

    # -- response.output_text.done ------------------------------------------
    yield ResponseTextDoneEvent(
        type="response.output_text.done",
        sequence_number=seq,
        item_id=msg_id,
        output_index=0,
        content_index=0,
        text=full_text,
        logprobs=[],
    )
    seq += 1

    # -- response.output_item.done ------------------------------------------
    completed_msg = ResponseOutputMessage(
        id=msg_id,
        type="message",
        role="assistant",
        status="completed",
        content=[
            ResponseOutputText(
                type="output_text",
                text=full_text,
                annotations=[],
            )
        ],
    )
    yield ResponseOutputItemDoneEvent(
        type="response.output_item.done",
        sequence_number=seq,
        output_index=0,
        item=completed_msg,
    )
    seq += 1

    # -- response.completed -------------------------------------------------
    resp_usage: Optional[ResponseUsage] = None
    if final_usage is not None:
        resp_usage = ResponseUsage(
            input_tokens=final_usage.prompt_tokens,
            output_tokens=final_usage.completion_tokens,
            total_tokens=final_usage.total_tokens,
            input_tokens_details=InputTokensDetails(cached_tokens=0),
            output_tokens_details=OutputTokensDetails(reasoning_tokens=0),
        )

    completed_resp = Response(
        id=response_id,
        created_at=created_at,
        model=model,
        object="response",
        output=[completed_msg],
        parallel_tool_calls=True,
        tool_choice="auto",
        tools=[],
        status="completed",
        usage=resp_usage,
    )
    yield ResponseCompletedEvent(
        type="response.completed",
        sequence_number=seq,
        response=completed_resp,
    )


# ---------------------------------------------------------------------------
# ChatResponsesProvider
# ---------------------------------------------------------------------------


class ChatResponsesProvider(BaseProvider):
    """Provider that bridges the Responses API to Chat Completions.

    Subclasses of this provider override every Responses-API method
    (``responses_create``, ``responses_parse``, ``responses_stream`` and
    their async counterparts) to:

    1. Convert the Responses-format *input* (plus optional *instructions*)
       into a Chat-Completions ``messages`` list.
    2. Map known Responses-API parameters to their Chat-Completions
       equivalents.
    3. Delegate to the native Chat-Completions endpoint.
    4. Convert the resulting ``ChatCompletion`` (or stream of
       ``ChatCompletionChunk``) into the Responses-API data shape.

    Providers whose backend servers do **not** expose a ``/v1/responses``
    endpoint should inherit from this class instead of directly from
    :class:`BaseProvider`, unless they need completely custom responses
    handling (e.g. provider-side multi-modal reasoning).
    """

    # ---- Internal helpers -------------------------------------------------

    @staticmethod
    def _extract_instructions(kwargs: Dict[str, Any]) -> Optional[str]:
        """Pop *instructions* from *kwargs* if present (does not mutate)."""
        return kwargs.pop("instructions", None)

    def _prepare_create_params(
        self, model: str, input_value: Any, **kwargs: Any
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Convert a single responses call into chat-style parameters.

        Returns ``(messages, chat_kwargs)``.
        """
        instructions = kwargs.pop("instructions", None)
        messages = responses_input_to_messages(input_value, instructions=instructions)
        chat_kwargs = _map_responses_kwargs_to_chat(kwargs)
        return messages, chat_kwargs

    # ---- Sync Responses API -----------------------------------------------

    def responses_create(
        self,
        model: str,
        input: Union[str, List[Dict[str, Any]]],
        **kwargs: Any,
    ) -> Response | Stream[ResponseStreamEvent]:
        model, input_value, new_kwargs = self._prepare_responses_call(
            model, input, **kwargs
        )
        stream = new_kwargs.get("stream", False)

        messages, chat_kwargs = self._prepare_create_params(
            model, input_value, **new_kwargs
        )

        if stream:
            if "stream" in chat_kwargs:
                chat_kwargs.pop("stream")
            chat_stream = self.chat_completions_create(
                model, messages, stream=True, **chat_kwargs
            )
            resp_id = _generate_id("resp_")
            msg_id = _generate_id("msg_")
            return _build_stream_events(chat_stream, resp_id, msg_id, model)

        chat_response = self.chat_completions_create(model, messages, **chat_kwargs)
        return chat_completion_to_response(chat_response)

    def responses_parse(
        self,
        model: str,
        input: Union[str, List[Dict[str, Any]]],
        **kwargs: Any,
    ):
        # Note: responses_parse returns a ParsedResponse which requires the
        # response_format parameter. We attempt to delegate to chat completions
        # parse if the provider supports it.
        model, input_value, new_kwargs = self._prepare_responses_call(
            model, input, **kwargs
        )
        messages, chat_kwargs = self._prepare_create_params(
            model, input_value, **new_kwargs
        )
        # Chat completions parse may be available on some providers
        try:
            return self.chat_completions_parse(model, messages, **chat_kwargs)
        except Exception:
            # Fallback: treat as regular create if parse is unsupported
            chat_response = self.chat_completions_create(
                model, messages, **chat_kwargs
            )
            return chat_completion_to_response(chat_response)

    def responses_stream(
        self,
        model: str,
        input: Union[str, List[Dict[str, Any]]],
        **kwargs: Any,
    ) -> Stream[ResponseStreamEvent]:
        """Stream a response through the chat-completions fallback.

        Returns a synchronous iterator of :class:`ResponseStreamEvent`.
        """
        model, input_value, new_kwargs = self._prepare_responses_call(
            model, input, **kwargs
        )
        messages, chat_kwargs = self._prepare_create_params(
            model, input_value, **new_kwargs
        )
        chat_stream = self.chat_completions_create(
            model, messages, stream=True, **chat_kwargs
        )
        resp_id = _generate_id("resp_")
        msg_id = _generate_id("msg_")
        return _build_stream_events(chat_stream, resp_id, msg_id, model)

    # ---- Async Responses API ----------------------------------------------

    async def async_responses_create(
        self,
        model: str,
        input: Union[str, List[Dict[str, Any]]],
        **kwargs: Any,
    ) -> Response | AsyncStream[ResponseStreamEvent]:
        model, input_value, new_kwargs = self._prepare_responses_call(
            model, input, **kwargs
        )
        stream = new_kwargs.get("stream", False)

        messages, chat_kwargs = self._prepare_create_params(
            model, input_value, **new_kwargs
        )

        if stream:
            chat_stream = await self.async_chat_completions_create(
                model, messages, stream=True, **chat_kwargs
            )
            resp_id = _generate_id("resp_")
            msg_id = _generate_id("msg_")
            return _build_async_stream_events(chat_stream, resp_id, msg_id, model)

        chat_response = await self.async_chat_completions_create(
            model, messages, **chat_kwargs
        )
        return chat_completion_to_response(chat_response)

    async def async_responses_parse(
        self,
        model: str,
        input: Union[str, List[Dict[str, Any]]],
        **kwargs: Any,
    ):
        model, input_value, new_kwargs = self._prepare_responses_call(
            model, input, **kwargs
        )
        messages, chat_kwargs = self._prepare_create_params(
            model, input_value, **new_kwargs
        )
        try:
            return await self.async_chat_completions_parse(
                model, messages, **chat_kwargs
            )
        except Exception:
            chat_response = await self.async_chat_completions_create(
                model, messages, **chat_kwargs
            )
            return chat_completion_to_response(chat_response)

    def async_responses_stream(
        self,
        model: str,
        input: Union[str, List[Dict[str, Any]]],
        **kwargs: Any,
    ) -> AsyncIterator[ResponseStreamEvent]:
        """Stream a response through the async chat-completions fallback.

        Returns an asynchronous generator of :class:`ResponseStreamEvent`.
        """
        # Async generators must use a different pattern — return the generator
        # immediately rather than awaiting.
        return self._async_responses_stream_impl(model, input, **kwargs)

    async def _async_responses_stream_impl(
        self,
        model: str,
        input: Union[str, List[Dict[str, Any]]],
        **kwargs: Any,
    ) -> AsyncIterator[ResponseStreamEvent]:
        """Coroutine that yields :class:`ResponseStreamEvent` items."""
        model, input_value, new_kwargs = self._prepare_responses_call(
            model, input, **kwargs
        )
        messages, chat_kwargs = self._prepare_create_params(
            model, input_value, **new_kwargs
        )
        chat_stream = await self.async_chat_completions_create(
            model, messages, stream=True, **chat_kwargs
        )
        resp_id = _generate_id("resp_")
        msg_id = _generate_id("msg_")
        async for event in _build_async_stream_events(
            chat_stream, resp_id, msg_id, model
        ):
            yield event