# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation & Dependencies

The project uses both Poetry and uv for dependency management (both supported by pyproject.toml):

```bash
# Install core dependencies only
uv sync
# or: poetry install

# Install all provider extras
uv sync --extra all
# or: poetry install --extras "all"

# Install with dev/test tools
uv sync --group dev --group test
# or: poetry install --with dev --with test --extras "all"
```

### Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=aisuite4cn
```

### Building & Distribution

```bash
# Build package (both uv and poetry are supported)
uv build
# or: poetry build
```

## Architecture Overview

`aisuite4cn` is a unified Python client library providing a standard OpenAI-compatible interface to Chinese LLM providers (DeepSeek, Qwen, Moonshot, Doubao, etc.). It wraps provider APIs behind a single `client.chat.completions.create(model="provider:model-name", ...)` call.

### Core Components

**`client.py`**: Main entry points with synchronous (`Client`) and asynchronous (`AsyncClient`) variants. Exposes three API interfaces:
- `chat.completions` - Chat completions (create, parse, stream)
- `embeddings` - Text embeddings
- `responses` - Responses API (create, parse, stream)

**`provider.py`**: Defines the `Provider` abstract base class (with all method signatures) and `ProviderFactory`. The factory dynamically loads providers based on a naming convention:
- Provider files: `aisuite4cn/providers/<snake_case>_provider.py`
- Provider classes: `<PascalCase>Provider`
- Example: `qwen_provider.py` → `QwenProvider` class

**`base_provider.py`**: Base class for most providers. Wraps the official OpenAI Python SDK, forwarding calls to `base_url` endpoints. Provides `client` and `async_client` properties using lazy initialization.

**`providers/`**: One file per provider (18 providers). Most extend `BaseProvider` (OpenAI-compatible). Non-trivial implementations:
- `qianfan_provider.py` - IAM authentication (Bearer token from `QIANFAN_ACCESS_KEY`/`QIANFAN_SECRET_KEY`)
- `ollama_provider.py` - Custom streaming parser (think-tag handling)
- `hermes_agent_provider.py` - Custom SSE decoder for tool progress events

**`framework/`**: Response dataclasses (ChatCompletionResponse, Choice, Message) conforming to OpenAI's response model.

### Model Naming Convention

Model strings use format `<provider>:<model-name>` (e.g., `qwen:qwen-max`, `deepseek:deepseek-chat`). The provider part is automatically converted to snake_case (e.g., `QwenProvider`) and the corresponding provider file is dynamically imported.

### Provider Configuration

Configuration is passed either via environment variables or via `provider_configs` dict in `Client.__init__`. Environment variable naming: `<PROVIDER>_API_KEY` (e.g., `DEEPSEEK_API_KEY`, `MOONSHOT_API_KEY`). Special cases:
- `SPARK_API_KEY_MAP` - Model-to-key mapping for Spark
- `QIANFAN_ACCESS_KEY`/`QIANFAN_SECRET_KEY` - For Qianfan IAM auth
- `OLLAMA_BASE_URL`/`HERMES_AGENT_BASE_URL`/`CUSTOM_BASE_URL` - Base URLs required for those providers

Configuration passed to `Client` takes precedence over environment variables.

### Framework Integrations (Optional)

The package includes optional integrations:
- `aisuite4cn/llama_index/` - LangChain-compatible
- `aisuite4cn/agentscope/` - AgentScope-compatible
- `examples/llama_index/` and `examples/agentscope/` - Example usage

## Adding a New Provider

1. Create `aisuite4cn/providers/<name>_provider.py` with class `<Name>Provider(BaseProvider)`
2. In `__init__(self, **config)`:
   - Set API key from config or environment variable (`<NAME>_API_KEY`)
   - Call `super().__init__(base_url, **config)` with the provider's base_url
3. Add provider's optional dependency to `pyproject.toml` under `[project.optional-dependencies]`
4. No registration needed - factory auto-discovers via filename convention

## Conventions & Gotchas

- **Base URL**: Most providers use a fixed base_url (defined in their provider file). For `ollama`, `hermes_agent`, and `custom`, you must provide `base_url` in config.
- **Dashscope/Qwen alias**: `dashscope_provider.py` and `qwen_provider.py` both use the same endpoint; `dashscope` is a thin alias.
- **Xiaomi/Mimo alias**: `xiaomi_provider.py` and `mimo_provider.py` are aliases for the same endpoint.
- **PyPI mirror**: Both `pyproject.toml` and `uv.lock` use Alibaba Cloud mirror (`https://mirrors.aliyun.com/pypi/simple`).
- **No test coverage**: The `tests/` directory exists but is essentially empty (no automated tests).
- **No linting/formatter**: No ruff, black, or mypy configured.

## Common Patterns

**Streaming responses**: The client delegates streaming to the provider. Most providers return OpenAI SDK streaming objects. For custom streaming logic (e.g., `ollama`), the provider implements `chat_completions_stream` returning a custom iterator.

**Custom kwargs handling**: `BaseProvider._compatible_with_openai_kwargs()` and `_compatible_with_responses_kwargs()` filter kwargs to only include supported OpenAI parameters, moving unknown parameters into `extra_body`.

**Async API**: All methods have both sync and async variants (`async_chat_completions_create`, `async_embeddings_create`, etc.). Use `AsyncClient` for async operations.