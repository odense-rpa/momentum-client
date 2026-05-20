from typing import Optional
from momentum_client.client import MomentumClient


class VitasClient:
    def __init__(self, client: MomentumClient):
        self._client = client
