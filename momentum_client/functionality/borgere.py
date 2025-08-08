from typing import Optional, List
from momentum_client.client import MomentumClient

class BorgereClient:
    def __init__(self, client: MomentumClient):
        self._client = client

    def hent_borger(self, cpr: str) -> Optional[dict]:
        """
        Fetch a citizen's data by their CPR number.

        :param cpr: Citizen's CPR number
        :return: Citizen data as a dictionary or None if not found
        """
        endpoint = f"citizens/find?cpr={cpr}"
        response = self._client.get(endpoint)
        if response.status_code == 404:
            return None
        return response.json()
    
    def hent_borgere(self, filters: dict, søgeterm = "*") -> Optional[dict]:
        """
        Hent borgere med angivne filtre og søgeterm.
        :param filters: Dictionary of filters to apply
        :param søgeterm: Search term to filter citizens. Default is * ("alle")
        :return: List of citizens matching the criteria or None if not found
        """
        endpoint = f"citizensearch"
        response = self._client.post(endpoint, json={"filters": filters, "søgeterm": søgeterm})
        if response.status_code == 404:
            return None
        return response.json()