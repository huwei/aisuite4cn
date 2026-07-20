# Build from project root:
#   docker build -f aisuite4cn/gateway/Dockerfile -t aisuite4cn-gateway .
#   docker run -p 8000:8000 -v /path/to/config.yaml:/app/config.yaml -e AISUITE_GATEWAY_CONFIG=/app/config.yaml aisuite4cn-gateway
#
# 或使用环境变量（不挂载配置文件）:
#   docker run -p 8000:8000 -e DEEPSEEK_API_KEY=xxx -e QWEN_API_KEY=yyy aisuite4cn-gateway

FROM python:3.12-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files (paths relative to build context = project root)
COPY pyproject.toml README.md ./

# Install Python dependencies
RUN pip install --no-cache-dir --index-url https://mirrors.aliyun.com/pypi/simple \
    fastapi>=0.115.0 \
    "uvicorn[standard]>=0.34.0" \
    click>=8.1.0 \
    pydantic>=2.10.3 \
    python-box>=7.3.2 \
    python-dotenv>=1.1.0 \
    httpx>=0.27.0 \
    openai>=2.44.0 \
    pyyaml>=6.0

# Copy application code
COPY aisuite4cn/ ./aisuite4cn/

# Create non-root user
RUN useradd --create-home --shell /bin/bash gateway
USER gateway

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the gateway (config via --config or AISUITE_GATEWAY_CONFIG env var)
CMD ["python", "-m", "aisuite4cn.gateway", "--host", "0.0.0.0", "--port", "8000"]
