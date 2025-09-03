from typing import Optional
from momentum_client.client import MomentumClient
import datetime


class MarkeringerClient:
    def __init__(self, client: MomentumClient):
        self._client = client

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

    def hent_markeringer(self, referenceId: str):
        
        endpoint = f"/tagassignments?referenceId={referenceId}"
        response = self._client.get(endpoint)
        if response.status_code == 404:
            return None
        return response.json()
    
    def opret_markering(self, markeringsnavn: str, referenceId: str, start_dato: datetime.date) -> Optional[dict]:
        """
        Opret en markering for en borger.
        
        :param referenceId på den borger eller virksomhed der ønskes at oprette markering på
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
        
        endpoint = f"/tagassignments?referenceId={referenceId}"
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
    
    def afslut_markering(self, markering: dict, slut_dato: datetime.date) -> Optional[dict]:
        """
        Afslutter en markering.

        :param Markering: den fulde markering som dict
        :param slut_dato: Slutdato for markeringen
        :return: Opdateret markering som dict eller None hvis fejlet
        """
        # Format slut_dato as yyyy-MM-ddT22:00:00Z
        formatted_slut_dato = slut_dato.strftime("%Y-%m-%dT00:00:00Z")

        body = {
            "tagId": f"{markering['tag']['id']}",
            "start": markering["start"],
            "end": f"{formatted_slut_dato}",
            "correctionComment": {
                "referenceId": f"{markering['id']}",
                "referenceType": None,
                "body": None,
                "title": None,
                "commentTypeCode": None
            },
            "attachmentsToAdd": [
            ],
            "attachmentsToRemove": [
            ]
        }

        endpoint = f"/tagassignments/{markering['id']}"
        response = self._client.put(endpoint, json=body)
        return response.json() if response.status_code == 200 else None
