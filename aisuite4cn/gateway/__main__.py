"""Module entry point for running the gateway via python -m aisuite4cn.gateway."""

import argparse
import os

import uvicorn

from .app import create_app
from .config import get_provider_configs


def main():
    """Run the gateway server directly."""
    parser = argparse.ArgumentParser(description="aisuite4cn Gateway Server")
    parser.add_argument("--host", default=os.environ.get("AISUITE_GATEWAY_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("AISUITE_GATEWAY_PORT", "8000")))
    parser.add_argument("--reload", action="store_true",
                        default=os.environ.get("AISUITE_GATEWAY_RELOAD", "false").lower() == "true")
    parser.add_argument("--config", "-c", default=os.environ.get("AISUITE_GATEWAY_CONFIG"),
                        help="Path to config file (.yaml or .json)")
    args = parser.parse_args()

    provider_configs = get_provider_configs(args.config)
    app = create_app(provider_configs=provider_configs)

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
