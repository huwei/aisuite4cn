import os
import time
from typing import Optional

import openai
from pydantic import BaseModel
from qianfan.resources.console.iam import IAM

from aisuite4cn import BaseProvider


class BearerToken(BaseModel):
    user_id: Optional[str] = None
    token: Optional[str] = None
    status: Optional[str] = None
    create_time: float = 0
    expire_time: float = 0


class QianfanProvider(BaseProvider):
    """
    Baidu Qianfan Provider

    ref: https://cloud.baidu.com/doc/WENXINWORKSHOP/s/em4tsqo3v
    """

    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    bearerToken: Optional[BearerToken] = None

    def __init__(self, **config):
        """
        Initialize the Qianfan provider with the given configuration.
        Pass the entire configuration dictionary to the Qianfan client constructor.
        """
        # Ensure access key and secret key is provided either in config or via environment variable

        self.config = dict(config)

        self.config.setdefault("api_key", os.getenv("QIANFAN_API_KEY"))

        if self.config['api_key']:
            self.use_api_key = True
            self.config.pop("access_key")
            self.config.pop("secret_key")
        else:
            self.use_api_key = False
            self.access_key = self.config.pop("access_key", os.getenv("QIANFAN_ACCESS_KEY"))
            self.secret_key = self.config.pop("secret_key", os.getenv("QIANFAN_SECRET_KEY"))
            if not self.access_key:
                raise ValueError(
                    "Qainfan access key is missing. Please provide it in the config or set the QIANFAN_ACCESS_KEY environment variable."
                )
            if not self.secret_key:
                raise ValueError(
                    "Qianfan secret key is missing. Please provide it in the config or set the QIANFAN_SECRET_KEY environment variable."
                )

        super().__init__(
            base_url='https://qianfan.baidubce.com/v2',
            **self.config)

    @property
    def client(self):
        """Getter for the OpenAI client."""
        if not self._client:
            if self.use_api_key:
                self._client = openai.OpenAI(base_url=self.base_url, **self.config)
            else:
                self._client = openai.OpenAI(
                    api_key=self.get_bearer_token(),
                    base_url=self.base_url,
                    **self.config)
            return self._client

        if not self.use_api_key:
            self._client.api_key = self.get_bearer_token()
        return self._client

    @property
    def async_client(self):
        """Getter for the asynchronous OpenAI client.

        Lazily initializes the AsyncOpenAI client if not already created.
        """
        if not self._async_client:
            if self.use_api_key:
                self._async_client = openai.AsyncOpenAI(
                    base_url=self.base_url,
                    **self.config
                )
            else:
                self._async_client = openai.AsyncOpenAI(
                    api_key=self.get_bearer_token(),
                    base_url=self.base_url,
                    **self.config
                )
            return self._async_client

        if not self.use_api_key:
            self._async_client.api_key = self.get_bearer_token()
        return self._async_client

    def get_bearer_token(self):
        if self.bearerToken is None:
            self.bearerToken = BearerToken()
        if time.time() < self.bearerToken.expire_time:
            return self.bearerToken.token

        os.environ["QIANFAN_ACCESS_KEY"] = self.access_key
        os.environ["QIANFAN_SECRET_KEY"] = self.secret_key
        expire_in_seconds = 86400
        response = IAM.create_bearer_token(expire_in_seconds=expire_in_seconds)
        self.bearerToken.user_id = response.body.get('user_id')
        self.bearerToken.token = response.body.get('token')
        self.bearerToken.status = response.body.get('enable')
        self.bearerToken.create_time = time.time()
        self.bearerToken.expire_time = self.bearerToken.create_time + expire_in_seconds - 120
        return self.bearerToken.token
