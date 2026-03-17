# Development Guide

pyproject.toml 文件现在完全符合 PEP 621 标准，并包含 uv 和 Poetry 都能识别和使用的配置。这确保了团队成员无论使用 poetry 还是 uv 都能获得一致的依赖管理体验。

#### 使用 Poetry：
```shell
poetry install --with dev
poetry install --with test
poetry install --extras "all"
poetry install --extras "all" --with dev
```

#### 使用 uv：
```shell
uv sync --group dev
uv sync --group test
uv sync --extra all
uv sync --extra all --group dev
```
