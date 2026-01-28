from typing import Optional
from momentum_client.client import MomentumClient
from typing import Optional, List


class TaksonomierClient:
    def __init__(self, client: MomentumClient):
        self._client = client
    
    def hent_alle_taksonomier(self) -> dict:
        endpoint = f"/taxonomies"

        respone = self._client.get(endpoint)

        return respone.json()


    def find_taksonomi_gruppe(self, taxanomi_kode:str) -> Optional[dict]:
        endpoint = f"/taxonomies/{taxanomi_kode}"

        response = self._client.get(endpoint)

        if response.status_code == 404:
            return None
        
        return response.json()