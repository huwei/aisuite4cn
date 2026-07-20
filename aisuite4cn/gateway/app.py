"""FastAPI application for aisuite4cn Gateway."""

import json
from typing import Any, AsyncGenerator, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from aisuite4cn.client import _get_provider_key_and_model_name
from aisuite4cn.provider import ProviderFactory

from .models import (
    ChatCompletionRequest,
    ModelInfo,
    ModelListResponse,
    ResponseRequest,
)


def create_app(provider_configs: Optional[Dict[str, Any]] = None, **kwargs) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        provider_configs: Optional dict of provider configurations.
            Example: {"deepseek": {"api_key": "xxx"}, "qwen": {"api_key": "yyy"}}

    Returns:
        Configured FastAPI application instance.
    """
    if provider_configs is None:
        provider_configs = {}

    app = FastAPI(
        title="aisuite4cn Gateway",
        description="Unified HTTP API Gateway for Chinese LLM providers",
        version="1.0.0",
    )

    _client = None
    _configs = provider_configs

    def get_client():
        """Get or create the aisuite4cn AsyncClient."""
        nonlocal _client
        if _client is None:
            from aisuite4cn import AsyncClient
            _client = AsyncClient(provider_configs=_configs)
        return _client

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "service": "aisuite4cn-gateway"}

    @app.get("/v1/models")
    async def list_models():
        """List all available models from supported providers."""
        supported = ProviderFactory.get_supported_providers()
        models = []
        for provider_key in sorted(supported):
            models.append(ModelInfo(
                id=f"{provider_key}:default",
                owned_by=provider_key,
            ))
        return ModelListResponse(data=models)

    @app.post("/v1/chat/completions")
    async def chat_completions(request: ChatCompletionRequest):
        """Chat Completions API endpoint.

        Compatible with OpenAI Chat Completions API format.
        Model format: 'provider:model-name' (e.g., 'deepseek:deepseek-chat')
        """
        try:
            provider_key, model_name = _get_provider_key_and_model_name(request.model)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        client = get_client()

        request_data = request.model_dump(exclude_none=True)
        messages = request_data.pop("messages")
        model = request_data.pop("model")
        stream = request_data.pop("stream", False)

        try:
            if stream:
                return StreamingResponse(
                    _stream_chat_completions(client, model, messages, request_data),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                    },
                )
            else:
                completion = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    **request_data,
                )
                return _convert_to_dict(completion)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Provider error: {str(e)}")

    @app.post("/v1/responses")
    async def responses(request: ResponseRequest):
        """Responses API endpoint.

        Compatible with OpenAI Responses API format.
        Model format: 'provider:model-name' (e.g., 'qwen:qwen-max')
        """
        try:
            provider_key, model_name = _get_provider_key_and_model_name(request.model)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        client = get_client()

        request_data = request.model_dump(exclude_none=True)
        input_data = request_data.pop("input")
        model = request_data.pop("model")
        stream = request_data.pop("stream", False)

        try:
            if stream:
                return StreamingResponse(
                    _stream_responses(client, model, input_data, request_data),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                    },
                )
            else:
                response = await client.responses.create(
                    model=model,
                    input=input_data,
                    **request_data,
                )
                return _convert_to_dict(response)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Provider error: {str(e)}")

    async def _stream_chat_completions(client, model: str, messages: list, params: dict) -> AsyncGenerator[str, None]:
        """Stream chat completions as SSE events."""
        try:
            stream = client.chat.completions.chat_completions_stream(
                model=model,
                messages=messages,
                **params,
            )
            async for chunk in stream:
                chunk_dict = _convert_to_dict(chunk)
                yield f"data: {json.dumps(chunk_dict, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            error_data = {"error": {"message": str(e), "type": "server_error"}}
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

    async def _stream_responses(client, model: str, input_data: Any, params: dict) -> AsyncGenerator[str, None]:
        """Stream responses as SSE events."""
        try:
            stream = client.responses.stream(
                model=model,
                input=input_data,
                **params,
            )
            async for event in stream:
                event_dict = _convert_to_dict(event)
                yield f"data: {json.dumps(event_dict, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            error_data = {"error": {"message": str(e), "type": "server_error"}}
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

    def _convert_to_dict(obj: Any) -> Any:
        """Convert OpenAI SDK objects to JSON-serializable dicts."""
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        elif hasattr(obj, "dict"):
            return obj.dict()
        elif hasattr(obj, "__dict__"):
            return {k: _convert_to_dict(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
        elif isinstance(obj, (list, tuple)):
            return [_convert_to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: _convert_to_dict(v) for k, v in obj.items()}
        return obj

    return app
