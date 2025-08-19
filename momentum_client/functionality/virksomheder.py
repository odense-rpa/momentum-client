from typing import Optional, List
import datetime
from momentum_client.client import MomentumClient


class VirksomhederClient:
    def __init__(self, client: MomentumClient):
        self._client = client

    def hent_virksomheder(self, filters: dict = None, søgeterm: str = "*") -> Optional[dict]:
        """
        Hent virksomheder med angivne filtre og søgeterm.
        
        :param filters: Dictionary of filters to apply (optional)
        :param søgeterm: Search term to filter production units. Default is * ("alle")
        :return: List of production units matching the criteria or None if not found
        """
        endpoint = "punits/searchproductionunits"
        
        # Prepare the request body
        body = {
            "søgeterm": søgeterm
        }
        
        # Add filters if provided
        if filters:
            body["filters"] = filters
        
        response = self._client.post(endpoint, json=body)
        
        if response.status_code == 404:
            return None
        
        return response.json()