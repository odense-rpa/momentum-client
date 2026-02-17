from typing import Optional

from momentum_client.client import MomentumClient


class JournalnotaterClient:
    def __init__(self, client: MomentumClient):
        self._client = client

    def hent_journalnotater(self, referenceid:str) -> Optional[dict]:
        
        endpoint = f"/journals/{referenceid}"
        
        response = self._client.get(endpoint)
        
        return response.json()