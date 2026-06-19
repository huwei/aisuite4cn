import time
import uuid

from openai.types.responses import (
    Response,
    ResponseFunctionToolCall,
    ResponseOutputMessage,
    ResponseOutputText,
    ResponseUsage,
)

from aisuite4cn.base_provider import BaseProvider


def _generate_id(prefix="resp"):
    """Generate a unique ID with the given prefix."""
    return f"{prefix}-{uuid.uuid4().hex[:24]}"


class ChatToResponsesProvider(BaseProvider):
    """将 Chat Completions API 转换为 Responses API 格式的适配器。

    适用于不支持 Responses API 的模型提供商，通过内部调用 Chat Completions API
    并将输入/输出转换为 Responses API 格式来实现兼容。

    支持的转换：
    - input (str/list) → messages
    - instructions → system message
    - function_call → tool_calls
    - function_call_output → role=tool message
    - text.format → response_format
    - max_output_tokens → max_completion_tokens
    - reasoning.effort → reasoning_effort
    - ChatCompletion → Response
    - ChatCompletionChunk 流 → ResponseStreamEvent 流

    不支持的 Responses API 特性（静默忽略）：
    - previous_response_id
    - background
    - conversation
    - include
    - truncation

    使用方式：
        # 作为独立 provider
        client = ai.Client(provider_configs={
            "chat_to_responses": {"base_url": "http://localhost:11434/v1"}
        })
        response = client.responses.create(
            model="chat_to_responses:qwen3:8b",
            input="Hello",
            instructions="You are helpful."
        )

        # 作为 mixin
        class MyProvider(ChatToResponsesProvider, DeepseekProvider):
            pass
    """

    # ---- Input Conversion (Responses API → Chat Completions) ----

    def _convert_input_to_messages(self, input, **kwargs):
        """将 Responses API 的 input 参数转换为 Chat Completions 的 messages。

        Args:
            input: Responses API 的 input 参数（str 或 list）
            **kwargs: Responses API 的其他参数

        Returns:
            (messages, chat_kwargs) 元组
        """
        chat_kwargs = {}
        messages = []

        # 处理 instructions → system message
        instructions = kwargs.pop("instructions", None)
        if instructions:
            messages.append({"role": "system", "content": instructions})

        # 处理 input
        if isinstance(input, str):
            messages.append({"role": "user", "content": input})
        elif isinstance(input, list):
            for item in input:
                msg = self._convert_input_item(item)
                if msg is not None:
                    messages.append(msg)

        # 处理 text.format → response_format
        text_config = kwargs.pop("text", None)
        if text_config and isinstance(text_config, dict):
            fmt = text_config.get("format")
            if fmt:
                chat_kwargs["response_format"] = self._convert_text_format_to_response_format(fmt)

        # 处理 max_output_tokens → max_completion_tokens
        max_output_tokens = kwargs.pop("max_output_tokens", None)
        if max_output_tokens is not None:
            chat_kwargs["max_completion_tokens"] = max_output_tokens

        # 处理 reasoning.effort → reasoning_effort
        reasoning = kwargs.pop("reasoning", None)
        if reasoning and isinstance(reasoning, dict):
            effort = reasoning.get("effort")
            if effort:
                chat_kwargs["reasoning_effort"] = effort

        # 传递兼容的参数
        for key in ("temperature", "top_p", "tools", "tool_choice",
                    "parallel_tool_calls", "metadata", "stop",
                    "presence_penalty", "frequency_penalty", "seed",
                    "stream", "stream_options", "store", "service_tier",
                    "prompt_cache_key", "safety_identifier", "user",
                    "timeout"):
            if key in kwargs:
                chat_kwargs[key] = kwargs.pop(key)

        # 不支持的参数静默忽略
        for unsupported in ("previous_response_id", "background",
                            "conversation", "include", "truncation",
                            "max_tool_calls", "prompt"):
            kwargs.pop(unsupported, None)

        return messages, chat_kwargs

    def _convert_input_item(self, item):
        """将单个 Responses API input item 转换为 Chat Completions message。"""
        if not isinstance(item, dict):
            # 可能是 Pydantic 模型
            if hasattr(item, "model_dump"):
                item = item.model_dump()
            else:
                return None

        item_type = item.get("type", "message")
        role = item.get("role")

        # 简单消息（EasyInputMessageParam / Message）
        if item_type == "message" or (item_type is None and role in ("user", "system", "developer", "assistant")):
            content = item.get("content")
            if isinstance(content, str):
                return {"role": role or "user", "content": content}
            elif isinstance(content, list):
                # 转换结构化 content
                converted = self._convert_content_parts(content)
                return {"role": role or "user", "content": converted}
            return {"role": role or "user", "content": content or ""}

        # function_call → assistant message with tool_calls
        if item_type == "function_call":
            call_id = item.get("call_id", "")
            name = item.get("name", "")
            arguments = item.get("arguments", "{}")
            return {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": call_id,
                    "type": "function",
                    "function": {"name": name, "arguments": arguments}
                }]
            }

        # function_call_output → tool message
        if item_type == "function_call_output":
            call_id = item.get("call_id", "")
            output = item.get("output", "")
            return {"role": "tool", "tool_call_id": call_id, "content": output}

        # 其他类型忽略
        return None

    def _convert_content_parts(self, parts):
        """将 Responses API 的 content parts 转换为 Chat Completions 格式。"""
        converted = []
        for part in parts:
            if isinstance(part, dict):
                part_type = part.get("type", "")
            elif hasattr(part, "type"):
                part_type = part.type
                part = part.model_dump() if hasattr(part, "model_dump") else {}
            else:
                continue

            if part_type == "input_text":
                text = part.get("text", "")
                converted.append({"type": "text", "text": text})
            elif part_type == "input_image":
                image_url = part.get("image_url", "")
                detail = part.get("detail", "auto")
                img_item = {"url": image_url}
                if detail:
                    img_item["detail"] = detail
                converted.append({"type": "image_url", "image_url": img_item})
            elif part_type == "text":
                converted.append({"type": "text", "text": part.get("text", "")})
            else:
                # 未知类型，尝试作为 text
                text = part.get("text", "")
                if text:
                    converted.append({"type": "text", "text": text})

        return converted if converted else ""

    @staticmethod
    def _convert_text_format_to_response_format(fmt):
        """将 Responses API 的 text.format 转换为 Chat Completions 的 response_format。"""
        if isinstance(fmt, dict):
            fmt_type = fmt.get("type", "text")
        elif hasattr(fmt, "type"):
            fmt_type = fmt.type
            fmt = fmt.model_dump() if hasattr(fmt, "model_dump") else {}
        else:
            return None

        if fmt_type == "json_object":
            return {"type": "json_object"}
        elif fmt_type == "json_schema":
            return {
                "type": "json_schema",
                "json_schema": {
                    "name": fmt.get("name", "response"),
                    "schema": fmt.get("schema", fmt.get("schema_", {})),
                    "strict": fmt.get("strict", True),
                }
            }
        # type="text" 或其他 → 不设置 response_format
        return None

    # ---- Non-streaming Output Conversion (ChatCompletion → Response) ----

    def _convert_chat_response_to_response(self, chat_response, model):
        """将 Chat Completions 响应转换为 Responses API 的 Response 对象。"""
        output = []

        for choice in chat_response.choices:
            message = choice.message

            # 处理 tool_calls → ResponseFunctionToolCall items
            if message.tool_calls:
                for tc in message.tool_calls:
                    output.append(ResponseFunctionToolCall(
                        id=_generate_id("fc"),
                        type="function_call",
                        call_id=tc.id,
                        name=tc.function.name,
                        arguments=tc.function.arguments,
                        status="completed",
                    ))

            # 处理文本内容 → ResponseOutputMessage
            content_text = message.content
            if content_text:
                output.append(ResponseOutputMessage(
                    id=_generate_id("msg"),
                    type="message",
                    role="assistant",
                    status="completed",
                    content=[ResponseOutputText(
                        type="output_text",
                        text=content_text,
                        annotations=[],
                    )],
                ))

        # 处理 usage
        usage = None
        if chat_response.usage:
            usage = ResponseUsage(
                input_tokens=chat_response.usage.prompt_tokens,
                input_tokens_details={"cached_tokens": 0},
                output_tokens=chat_response.usage.completion_tokens,
                output_tokens_details={"reasoning_tokens": 0},
                total_tokens=chat_response.usage.total_tokens,
            )

        response_id = chat_response.id.replace("chatcmpl-", "resp-") if chat_response.id else _generate_id("resp")

        return Response(
            id=response_id,
            object="response",
            created_at=chat_response.created or int(time.time()),
            model=model or chat_response.model,
            status="completed",
            output=output,
            usage=usage,
            parallel_tool_calls=True,
            tool_choice="auto",
            tools=[],
        )

    # ---- Streaming Output Conversion (ChatCompletionChunk → ResponseStreamEvent) ----

    def _convert_stream_to_response_events(self, stream, model):
        """将 Chat Completions 流式响应转换为 Responses API 流式事件。"""
        seq = 0
        response_id = None
        created_at = int(time.time())
        msg_item_id = _generate_id("msg")
        text_accumulated = []

        # 收集 tool call 信息
        tool_calls_info = {}  # index -> {id, name, arguments, item_id}

        has_started = False
        has_content_part = False

        for chunk in stream:
            if not chunk.choices:
                # 可能是 usage-only chunk
                continue

            choice = chunk.choices[0]
            delta = choice.delta

            if not response_id and chunk.id:
                response_id = chunk.id.replace("chatcmpl-", "resp-")
            if not response_id:
                response_id = _generate_id("resp")

            # 首个 chunk → 发送 response lifecycle 事件
            if not has_started:
                has_started = True

                # response.created
                yield self._make_event("response.created", seq, response={
                    "id": response_id, "object": "response", "created_at": created_at,
                    "model": model, "status": "queued", "output": [],
                    "parallel_tool_calls": True, "tool_choice": "auto", "tools": [],
                })
                seq += 1

                # response.in_progress
                yield self._make_event("response.in_progress", seq, response={
                    "id": response_id, "object": "response", "created_at": created_at,
                    "model": model, "status": "in_progress", "output": [],
                    "parallel_tool_calls": True, "tool_choice": "auto", "tools": [],
                })
                seq += 1

            # 处理 tool_calls in delta
            if delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    tc_index = tc_delta.index

                    if tc_index not in tool_calls_info:
                        # 新的 tool call 开始
                        tc_item_id = _generate_id("fc")
                        tool_calls_info[tc_index] = {
                            "id": tc_item_id,
                            "call_id": getattr(tc_delta, "id", None) or _generate_id("call"),
                            "name": "",
                            "arguments": "",
                            "item_id": tc_item_id,
                            "output_index": len(tool_calls_info),
                        }

                        # 如果还没开始 content part，先关闭它
                        # (content part 和 tool call 是不同的 output items)

                        # response.output_item.added (function_call)
                        yield self._make_event("response.output_item.added", seq,
                                               item={
                                                   "type": "function_call",
                                                   "id": tc_item_id,
                                                   "call_id": tool_calls_info[tc_index]["call_id"],
                                                   "name": getattr(tc_delta.function, "name", "") or "",
                                                   "arguments": "",
                                                   "status": "in_progress",
                                               },
                                               output_index=tool_calls_info[tc_index]["output_index"])
                        seq += 1

                    info = tool_calls_info[tc_index]

                    # 更新 name
                    if hasattr(tc_delta.function, "name") and tc_delta.function.name:
                        info["name"] = tc_delta.function.name

                    # 更新 call_id
                    if hasattr(tc_delta, "id") and tc_delta.id:
                        info["call_id"] = tc_delta.id

                    # 处理 arguments delta
                    if hasattr(tc_delta.function, "arguments") and tc_delta.function.arguments:
                        info["arguments"] += tc_delta.function.arguments

                        # response.function_call_arguments.delta
                        yield self._make_event("response.function_call_arguments.delta", seq,
                                               item_id=info["item_id"],
                                               output_index=info["output_index"],
                                               delta=tc_delta.function.arguments)
                        seq += 1

            # 处理 content delta
            if delta.content:
                # 如果还没创建 content part，先创建 message item 和 content part
                if not has_content_part:
                    has_content_part = True
                    output_index = len(tool_calls_info) if tool_calls_info else 0

                    # response.output_item.added (message)
                    yield self._make_event("response.output_item.added", seq,
                                           item={
                                               "type": "message",
                                               "id": msg_item_id,
                                               "role": "assistant",
                                               "status": "in_progress",
                                               "content": [],
                                           },
                                           output_index=output_index)
                    seq += 1

                    # response.content_part.added
                    yield self._make_event("response.content_part.added", seq,
                                           item_id=msg_item_id,
                                           output_index=output_index,
                                           content_index=0,
                                           part={"type": "output_text", "text": "", "annotations": []})
                    seq += 1

                text_accumulated.append(delta.content)

                # response.output_text.delta
                yield self._make_event("response.output_text.delta", seq,
                                       item_id=msg_item_id,
                                       output_index=0,
                                       content_index=0,
                                       delta=delta.content)
                seq += 1

            # 处理 finish_reason
            finish_reason = choice.finish_reason
            if finish_reason:
                full_text = "".join(text_accumulated)

                # 关闭 content part
                if has_content_part:
                    # response.output_text.done
                    yield self._make_event("response.output_text.done", seq,
                                           item_id=msg_item_id,
                                           output_index=0,
                                           content_index=0,
                                           text=full_text)
                    seq += 1

                    # response.content_part.done
                    yield self._make_event("response.content_part.done", seq,
                                           item_id=msg_item_id,
                                           output_index=0,
                                           content_index=0,
                                           part={"type": "output_text", "text": full_text, "annotations": []})
                    seq += 1

                    # response.output_item.done (message)
                    yield self._make_event("response.output_item.done", seq,
                                           item={
                                               "type": "message",
                                               "id": msg_item_id,
                                               "role": "assistant",
                                               "status": "completed",
                                               "content": [
                                                   {"type": "output_text", "text": full_text, "annotations": []}],
                                           },
                                           output_index=0)
                    seq += 1

                # 关闭 tool call items
                for tc_index in sorted(tool_calls_info.keys()):
                    info = tool_calls_info[tc_index]

                    # response.function_call_arguments.done
                    yield self._make_event("response.function_call_arguments.done", seq,
                                           item_id=info["item_id"],
                                           output_index=info["output_index"],
                                           arguments=info["arguments"])
                    seq += 1

                    # response.output_item.done (function_call)
                    yield self._make_event("response.output_item.done", seq,
                                           item={
                                               "type": "function_call",
                                               "id": info["item_id"],
                                               "call_id": info["call_id"],
                                               "name": info["name"],
                                               "arguments": info["arguments"],
                                               "status": "completed",
                                           },
                                           output_index=info["output_index"])
                    seq += 1

                # 构建 final response
                output = []

                # Tool calls come first in output
                for tc_index in sorted(tool_calls_info.keys()):
                    info = tool_calls_info[tc_index]
                    output.append({
                        "type": "function_call",
                        "id": info["item_id"],
                        "call_id": info["call_id"],
                        "name": info["name"],
                        "arguments": info["arguments"],
                        "status": "completed",
                    })

                # Then message
                if full_text or not tool_calls_info:
                    output.append({
                        "type": "message",
                        "id": msg_item_id,
                        "role": "assistant",
                        "status": "completed",
                        "content": [{"type": "output_text", "text": full_text, "annotations": []}],
                    })

                # Build usage
                usage_dict = None
                if hasattr(chunk, "usage") and chunk.usage:
                    usage_dict = {
                        "input_tokens": chunk.usage.prompt_tokens,
                        "input_tokens_details": {"cached_tokens": 0},
                        "output_tokens": chunk.usage.completion_tokens,
                        "output_tokens_details": {"reasoning_tokens": 0},
                        "total_tokens": chunk.usage.total_tokens,
                    }

                final_response = {
                    "id": response_id, "object": "response", "created_at": created_at,
                    "model": model, "status": "completed", "output": output,
                    "parallel_tool_calls": True, "tool_choice": "auto", "tools": [],
                }
                if usage_dict:
                    final_response["usage"] = usage_dict

                # response.completed
                yield self._make_event("response.completed", seq,
                                       response=final_response)
                seq += 1

    @staticmethod
    def _make_event(event_type, sequence_number, **fields):
        """构建一个 ResponseStreamEvent 兼容的 dict 对象。"""
        event = {"type": event_type, "sequence_number": sequence_number}
        event.update(fields)
        return event

    # ---- Responses API Method Overrides ----

    def responses_create(self, model, input, **kwargs):
        """通过 Chat Completions API 实现 Responses API 的 create。"""
        stream = kwargs.get("stream", False)
        messages, chat_kwargs = self._convert_input_to_messages(input, **kwargs)

        if stream:
            chat_kwargs["stream"] = True
            chat_stream = self.chat_completions_create(model, messages, **chat_kwargs)
            return self._convert_stream_to_response_events(chat_stream, model)

        chat_response = self.chat_completions_create(model, messages, **chat_kwargs)
        return self._convert_chat_response_to_response(chat_response, model)

    def responses_parse(self, model, input, **kwargs):
        """通过 Chat Completions API 实现 Responses API 的 parse。"""
        # responses_parse 使用 text_format 而非 text.format
        text_format = kwargs.pop("text_format", None)
        messages, chat_kwargs = self._convert_input_to_messages(input, **kwargs)

        if text_format:
            # 将 text_format (Pydantic model class) 传给 chat_completions_parse
            chat_response = self.chat_completions_parse(
                model, messages, response_format=text_format, **chat_kwargs
            )
        else:
            chat_response = self.chat_completions_parse(model, messages, **chat_kwargs)

        return self._convert_chat_response_to_response(chat_response, model)

    def responses_stream(self, model, input, **kwargs):
        """通过 Chat Completions API 实现 Responses API 的 stream。

        返回一个生成器，产生 ResponseStreamEvent 兼容的 dict。
        """
        messages, chat_kwargs = self._convert_input_to_messages(input, **kwargs)
        chat_kwargs["stream"] = True
        chat_stream = self.chat_completions_stream(model, messages, **chat_kwargs)
        return self._convert_stream_to_response_events(chat_stream, model)

    async def async_responses_create(self, model, input, **kwargs):
        """通过 Chat Completions API 实现 Responses API 的 async create。"""
        stream = kwargs.get("stream", False)
        messages, chat_kwargs = self._convert_input_to_messages(input, **kwargs)

        if stream:
            chat_kwargs["stream"] = True
            chat_stream = self.async_chat_completions_stream(model, messages, **chat_kwargs)
            return self._convert_async_stream_to_response_events(chat_stream, model)

        chat_response = await self.async_chat_completions_create(model, messages, **chat_kwargs)
        return self._convert_chat_response_to_response(chat_response, model)

    async def async_responses_parse(self, model, input, **kwargs):
        """通过 Chat Completions API 实现 Responses API 的 async parse。"""
        text_format = kwargs.pop("text_format", None)
        messages, chat_kwargs = self._convert_input_to_messages(input, **kwargs)

        if text_format:
            chat_response = await self.async_chat_completions_parse(
                model, messages, response_format=text_format, **chat_kwargs
            )
        else:
            chat_response = await self.async_chat_completions_parse(model, messages, **chat_kwargs)

        return self._convert_chat_response_to_response(chat_response, model)

    def async_responses_stream(self, model, input, **kwargs):
        """通过 Chat Completions API 实现 Responses API 的 async stream。"""
        messages, chat_kwargs = self._convert_input_to_messages(input, **kwargs)
        chat_kwargs["stream"] = True
        chat_stream = self.async_chat_completions_stream(model, messages, **chat_kwargs)
        return self._convert_async_stream_to_response_events(chat_stream, model)

    # ---- Async Streaming Conversion ----

    async def _convert_async_stream_to_response_events(self, stream, model):
        """将异步 Chat Completions 流式响应转换为 Responses API 流式事件。"""
        seq = 0
        response_id = None
        created_at = int(time.time())
        msg_item_id = _generate_id("msg")
        text_accumulated = []
        tool_calls_info = {}
        has_started = False
        has_content_part = False

        async for chunk in stream:
            if not chunk.choices:
                continue

            choice = chunk.choices[0]
            delta = choice.delta

            if not response_id and chunk.id:
                response_id = chunk.id.replace("chatcmpl-", "resp-")
            if not response_id:
                response_id = _generate_id("resp")

            if not has_started:
                has_started = True

                yield self._make_event("response.created", seq, response={
                    "id": response_id, "object": "response", "created_at": created_at,
                    "model": model, "status": "queued", "output": [],
                    "parallel_tool_calls": True, "tool_choice": "auto", "tools": [],
                })
                seq += 1

                yield self._make_event("response.in_progress", seq, response={
                    "id": response_id, "object": "response", "created_at": created_at,
                    "model": model, "status": "in_progress", "output": [],
                    "parallel_tool_calls": True, "tool_choice": "auto", "tools": [],
                })
                seq += 1

            if delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    tc_index = tc_delta.index

                    if tc_index not in tool_calls_info:
                        tc_item_id = _generate_id("fc")
                        tool_calls_info[tc_index] = {
                            "id": tc_item_id,
                            "call_id": getattr(tc_delta, "id", None) or _generate_id("call"),
                            "name": "",
                            "arguments": "",
                            "item_id": tc_item_id,
                            "output_index": len(tool_calls_info),
                        }

                        yield self._make_event("response.output_item.added", seq,
                                               item={
                                                   "type": "function_call",
                                                   "id": tc_item_id,
                                                   "call_id": tool_calls_info[tc_index]["call_id"],
                                                   "name": getattr(tc_delta.function, "name", "") or "",
                                                   "arguments": "",
                                                   "status": "in_progress",
                                               },
                                               output_index=tool_calls_info[tc_index]["output_index"])
                        seq += 1

                    info = tool_calls_info[tc_index]

                    if hasattr(tc_delta.function, "name") and tc_delta.function.name:
                        info["name"] = tc_delta.function.name

                    if hasattr(tc_delta, "id") and tc_delta.id:
                        info["call_id"] = tc_delta.id

                    if hasattr(tc_delta.function, "arguments") and tc_delta.function.arguments:
                        info["arguments"] += tc_delta.function.arguments

                        yield self._make_event("response.function_call_arguments.delta", seq,
                                               item_id=info["item_id"],
                                               output_index=info["output_index"],
                                               delta=tc_delta.function.arguments)
                        seq += 1

            if delta.content:
                if not has_content_part:
                    has_content_part = True
                    output_index = len(tool_calls_info) if tool_calls_info else 0

                    yield self._make_event("response.output_item.added", seq,
                                           item={
                                               "type": "message", "id": msg_item_id,
                                               "role": "assistant", "status": "in_progress", "content": [],
                                           },
                                           output_index=output_index)
                    seq += 1

                    yield self._make_event("response.content_part.added", seq,
                                           item_id=msg_item_id,
                                           output_index=output_index,
                                           content_index=0,
                                           part={"type": "output_text", "text": "", "annotations": []})
                    seq += 1

                text_accumulated.append(delta.content)

                yield self._make_event("response.output_text.delta", seq,
                                       item_id=msg_item_id, output_index=0, content_index=0,
                                       delta=delta.content)
                seq += 1

            finish_reason = choice.finish_reason
            if finish_reason:
                full_text = "".join(text_accumulated)

                if has_content_part:
                    yield self._make_event("response.output_text.done", seq,
                                           item_id=msg_item_id, output_index=0, content_index=0,
                                           text=full_text)
                    seq += 1

                    yield self._make_event("response.content_part.done", seq,
                                           item_id=msg_item_id, output_index=0, content_index=0,
                                           part={"type": "output_text", "text": full_text, "annotations": []})
                    seq += 1

                    yield self._make_event("response.output_item.done", seq,
                                           item={
                                               "type": "message", "id": msg_item_id,
                                               "role": "assistant", "status": "completed",
                                               "content": [
                                                   {"type": "output_text", "text": full_text, "annotations": []}],
                                           },
                                           output_index=0)
                    seq += 1

                for tc_index in sorted(tool_calls_info.keys()):
                    info = tool_calls_info[tc_index]

                    yield self._make_event("response.function_call_arguments.done", seq,
                                           item_id=info["item_id"],
                                           output_index=info["output_index"],
                                           arguments=info["arguments"])
                    seq += 1

                    yield self._make_event("response.output_item.done", seq,
                                           item={
                                               "type": "function_call",
                                               "id": info["item_id"],
                                               "call_id": info["call_id"],
                                               "name": info["name"],
                                               "arguments": info["arguments"],
                                               "status": "completed",
                                           },
                                           output_index=info["output_index"])
                    seq += 1

                output = []
                for tc_index in sorted(tool_calls_info.keys()):
                    info = tool_calls_info[tc_index]
                    output.append({
                        "type": "function_call", "id": info["item_id"],
                        "call_id": info["call_id"], "name": info["name"],
                        "arguments": info["arguments"], "status": "completed",
                    })

                if full_text or not tool_calls_info:
                    output.append({
                        "type": "message", "id": msg_item_id,
                        "role": "assistant", "status": "completed",
                        "content": [{"type": "output_text", "text": full_text, "annotations": []}],
                    })

                usage_dict = None
                if hasattr(chunk, "usage") and chunk.usage:
                    usage_dict = {
                        "input_tokens": chunk.usage.prompt_tokens,
                        "input_tokens_details": {"cached_tokens": 0},
                        "output_tokens": chunk.usage.completion_tokens,
                        "output_tokens_details": {"reasoning_tokens": 0},
                        "total_tokens": chunk.usage.total_tokens,
                    }

                final_response = {
                    "id": response_id, "object": "response", "created_at": created_at,
                    "model": model, "status": "completed", "output": output,
                    "parallel_tool_calls": True, "tool_choice": "auto", "tools": [],
                }
                if usage_dict:
                    final_response["usage"] = usage_dict

                yield self._make_event("response.completed", seq, response=final_response)
                seq += 1
