# AGENTS.md

## What this is

`aisuite4cn` is a Python client library that provides a uniform OpenAI-compatible interface to Chinese LLM providers (DeepSeek, Qwen, Moonshot, Doubao, etc.). It wraps each provider's API behind a single `client.chat.completions.create(model="provider:model-name", ...)` call.

## Quick commands

```shell
# Install with all provider extras and dev tools
uv sync --extra all --group dev --group test

# Run tests
pytest

# Build
uv build
# or: poetry build
```

There is no linter, formatter, or type checker configured in this repo.

## Architecture

Model strings use format `provider:model-name` (e.g., `qwen:qwen-max`, `deepseek:deepseek-chat`). The provider key is resolved to a file `aisuite4cn/providers/<snake_case_key>_provider.py` containing class `<PascalCaseKey>Provider`.

- `aisuite4cn/client.py` — `Client` and `AsyncClient` entrypoints
- `aisuite4cn/provider.py` — `Provider` ABC and `ProviderFactory` (dynamic import by naming convention)
- `aisuite4cn/base_provider.py` — `BaseProvider` base class; wraps the OpenAI Python SDK for OpenAI-compatible endpoints
- `aisuite4cn/providers/` — one file per provider; each reads its API key from an env var
- `aisuite4cn/framework/` — response dataclasses
- `aisuite4cn/llama_index/`, `aisuite4cn/agentscope/` — framework integrations (optional)

## Adding a new provider

1. Create `aisuite4cn/providers/<name>_provider.py`
2. Define `class <Name>Provider(BaseProvider)` with `__init__(self, **config)` that sets `api_key` from env and calls `super().__init__(base_url, **config)`
3. Add the provider's optional dependency in `pyproject.toml` under `[project.optional-dependencies]`
4. The factory auto-discovers it by filename convention — no registration step needed

## Conventions

- Most providers are OpenAI-compatible and extend `BaseProvider` (which uses the `openai` SDK). Only `qianfan` and `agentscope` have non-trivial implementations.
- Env var naming: `<PROVIDER>_API_KEY` (e.g., `DEEPSEEK_API_KEY`, `MOONSHOT_API_KEY`). Special cases: `ARK_MODEL_MAP` for Doubao, `SPARK_API_KEY_MAP` for Spark.
- The PyPI mirror is set to Alibaba Cloud (`mirrors.aliyun.com`) in both `pyproject.toml` and `uv.lock`.

## Gotchas

- The `tests/` directory is essentially empty (only `__init__.py`). There are no automated tests.
- `poetry.lock` and `uv.lock` are both gitignored. Dependencies are not locked in the repo.
