from typing import Optional, List
import datetime
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
    
    def hent_markering(self, markeringsnavn = "ØF-JC-AC-IT-emnebank") -> Optional[dict]:
        """
        Hent specifik markering baseret på markeringsnavn.
        
        :param markeringsnavn: Navnet på markeringen
        :return: Markeringsdata som en Dict eller None hvis ikke fundet
        """

        endpoint = f"/tags"
        response = self._client.get(endpoint)
        if response.status_code == 404:
            return None
        tags = response.json()
        ønsket_markering = next((tag for tag in tags if tag.get("title") == markeringsnavn), None)
        if ønsket_markering is None:
            return None
        return ønsket_markering
    
    def opret_markering(self, markeringsnavn: str, borger: dict, start_dato: datetime.date) -> Optional[dict]:
        """
        Opret en markering for en borger.
        
        :param markeringsnavn: Navnet på markeringen
        :param borger: Borgerens data som en Dict
        :param start_dato: Startdato for markeringen
        :return: Oprettet markering som en Dict eller None hvis fejlet
        """
        markering = self.hent_markering(markeringsnavn)
        if markering is None:
            raise ValueError(f"Markering '{markeringsnavn}' findes ikke.")
        
        body = {
            "createdAt": None,
            "updatedAt": None,
            "start": f"{start_dato}",
            "end": None,
            "tagId": markering["id"],
            "correctionComment": None,
            "attachmentsToAdd": [],
            "attachmentsToRemove": []
        }
        
        endpoint = f"/tagassignments?referenceId={borger['citizenId']}"
        response = self._client.post(endpoint, json=body)

        if response.status_code == 404:
            return None
        return response.json() if response.status_code == 201 else None
    
    def slet_markering(self, markerings_id: str) -> bool:
        """
        Slet en markering baseret på markerings ID.

        :param markerings_id: ID'et for markeringen der skal slettes
        :return: True hvis markeringen blev slettet, ellers False
        """
        endpoint = f"/tagassignments/{markerings_id}/delete"
        response = self._client.post(endpoint)
        return response.status_code == 200

