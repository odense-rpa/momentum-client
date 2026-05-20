from typing import Optional, List
from momentum_client.client import MomentumClient


class VitasClient:
    def __init__(self, client: MomentumClient):
        self._client = client

    def hent_vitas(self, søgeterm: str = "*") -> Optional[List[dict]]:
        """
        Hent VITAS-poster med angivet søgeterm.

        :param søgeterm: Søgeterm til filtrering. Standard er * ("alle")
        :return: Liste af VITAS-poster eller None hvis ikke fundet
        """
        endpoint = "/vitas/searchvitas"
        all_data = []
        page_number = 0
        has_more = True

        while has_more:
            term = søgeterm or "*"
            if not term.endswith("*"):
                term = term + "* "
            body = {
                "sort": [{"fieldName": "title", "ascending": False}],
                "paging": {"pageNumber": page_number, "pageSize": 1000},
                "columns": [],
                "searchFields": ["type"],
                "filters": [],
                "term": term,
                "impersonateCaseworkerId": None
            }
            response = self._client.post(endpoint, json=body)
            if response.status_code == 404:
                return None
            data = response.json()
            all_data.extend(data.get("data", []))
            has_more = data.get("hasMore", False)
            page_number += 1

        return all_data

    def hent_vita(self, id: str, type: str = "personalassistance" ) -> Optional[dict]:
        """
        Hent en specifik VITAS-bevilling baseret på ID.

        :param id: ID for den ønskede VITAS-bevilling
        :param type: Type af VITAS-bevilling (standard er "personalassistance")
        :return: VITAS-bevilling som dict eller None hvis ikke fundet
        """
        endpoint = f"/vitas/{type}/{id}"
        response = self._client.get(endpoint)
        if response.status_code == 404:
            return None
        return response.json()