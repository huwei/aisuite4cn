import os

from aisuite4cn.base_provider import BaseProvider


class OpenclawProvider(BaseProvider):
    """
    OpenClaw 网关的 OpenAI 兼容聊天补全 Provider。

    OpenClaw 的 Gateway 网关对外提供一个小型的 OpenAI 兼容表面
    (POST /v1/chat/completions、GET /v1/models、POST /v1/embeddings、
    POST /v1/responses 等)，底层请求会作为普通 Gateway 网关智能体运行。

    由于网关为自托管，监听的主机与端口由部署决定，因此 base_url 必须通过
    config 或环境变量 OPENCLAW_BASE_URL 提供。

    认证使用 Gateway 网关认证配置，常见为共享密钥模式
    (gateway.auth.mode="token" 或 "password")：
        Authorization: Bearer <token-or-password>
    对应 OPENCLAW_API_KEY (或 OPENCLAW_GATEWAY_TOKEN / OPENCLAW_GATEWAY_PASSWORD)。
    当 gateway.auth.mode="none" 时无需认证，api_key 可使用任意占位值。

    参考: https://docs.openclaw.ai/zh-CN/gateway/openai-http-api
    """

    def __init__(self, **config):
        """
        使用给定配置初始化 OpenClaw provider。
        将整个配置字典透传给底层的 OpenAI 客户端构造函数。
        """
        current_config = dict(config)

        base_url = current_config.pop("base_url", os.getenv("OPENCLAW_BASE_URL"))
        if not base_url:
            raise ValueError(
                "OpenClaw Base Url is missing. Please provide it in the config or set the OPENCLAW_BASE_URL environment variable."
            )

        # 共享密钥认证模式下需提供 token/password；none 模式下使用占位值即可。
        current_config["api_key"] = current_config.get(
            "api_key",
            os.getenv("OPENCLAW_API_KEY")
            or os.getenv("OPENCLAW_GATEWAY_TOKEN")
            or os.getenv("OPENCLAW_GATEWAY_PASSWORD")
            or "openclaw",
        )

        super().__init__(base_url, **current_config)
