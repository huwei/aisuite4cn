"""FastAPI application for aisuite4cn Gateway."""

import asyncio
import json
import time
from typing import Any, AsyncGenerator, Dict, List, Optional

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


def create_app(
    provider_configs: Optional[Dict[str, Any]] = None,
    config_path: Optional[str] = None,
    **kwargs,
) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        provider_configs: Optional dict of provider configurations.
            Example: {"deepseek": {"api_key": "xxx"}, "qwen": {"api_key": "yyy"}}
        config_path: Optional path to a config file. Used to resolve the default
            config location for lazy provider initialization.

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
    _config_path = config_path

    # Cache for /v1/models results
    _models_cache: Optional[Dict[str, Any]] = None
    _models_cache_time: float = 0
    MODELS_CACHE_TTL = 300  # 5 minutes

    def get_client():
        """Get or create the aisuite4cn AsyncClient."""
        nonlocal _client
        if _client is None:
            from aisuite4cn import AsyncClient
            _client = AsyncClient(provider_configs=_configs)
        return _client

    def _get_all_provider_configs() -> Dict[str, Any]:
        """Get the merged provider configs (explicit + default file)."""
        configs = dict(_configs)
        # Also load from default config file if exists
        from .config import DEFAULT_CONFIG_PATH, get_provider_configs
        if not _config_path and DEFAULT_CONFIG_PATH.exists():
            file_configs = get_provider_configs(str(DEFAULT_CONFIG_PATH))
            for key, val in file_configs.items():
                if key not in configs:
                    configs[key] = val
        return configs

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "service": "aisuite4cn-gateway"}

    @app.get("/v1/models")
    async def list_models():
        """List all models by querying each provider's /v1/models endpoint.

        Results are cached for 5 minutes. Each provider's models are fetched
        concurrently using async IO.
        """
        nonlocal _models_cache, _models_cache_time

        # Return cached results if still valid
        if _models_cache is not None and (time.time() - _models_cache_time) < MODELS_CACHE_TTL:
            return _models_cache

        configs = _get_all_provider_configs()
        if not configs:
            return ModelListResponse(data=[])

        # Fetch models from each provider concurrently
        all_models: List[ModelInfo] = []
        semaphore = asyncio.Semaphore(10)  # Limit concurrent connections

        async def fetch_provider_models(provider_key: str, config: Dict[str, Any]):
            async with semaphore:
                try:
                    provider = ProviderFactory.create_provider(provider_key, config)
                    if hasattr(provider, 'async_client') and provider.async_client:
                        response = await provider.async_client.models.list()
                        models = []
                        for model in response.data:
                            models.append(ModelInfo(
                                id=f"{provider_key}:{model.id}",
                                owned_by=provider_key,
                                created=getattr(model, 'created', 0) or 0,
                            ))
                        return models
                except Exception:
                    # Provider doesn't support /v1/models or auth failed - skip
                    pass
                return []

        tasks = [
            fetch_provider_models(key, config)
            for key, config in configs.items()
        ]
        results = await asyncio.gather(*tasks)

        for models in results:
            all_models.extend(models)

        # Sort by id for consistent output
        all_models.sort(key=lambda m: m.id)

        response = ModelListResponse(data=all_models)
        _models_cache = response
        _models_cache_time = time.time()
        return response

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
