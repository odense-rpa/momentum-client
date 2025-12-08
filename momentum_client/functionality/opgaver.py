from datetime import datetime
from momentum_client.client import MomentumClient

class OpgaverClient:
    def __init__(self, client: MomentumClient):
        self._client = client

    def opret_opgave(self, borger: dict, medarbejdere: list[dict], forfaldsdato: datetime, titel: str, beskrivelse: str) -> dict:
        """
        Opret en opgave for en given borger.

        :param borger: Borger objekt eller ID
        :param medarbejdere: Liste af medarbejder objekter eller IDs
        :param forfaldsdato: Dato for opgavens forfald
        :param titel: Titel på opgaven
        :param beskrivelse: Beskrivelse af opgaven
        :return: Opgave information som dictionary
        """

        opgave_skabelon = {            
            "title": titel,
            "description": beskrivelse,
            "deadline": forfaldsdato.isoformat(),
            "assignedActorsId": [medarbejder["id"] if isinstance(medarbejder, dict) else medarbejder for medarbejder in medarbejdere],
            "taskType": None,
            "reference": {
                "id": borger["id"] if isinstance(borger, dict) else borger, # TODO: Udvid til at kunne håndtere andre typer referencer
                "type": "CITIZEN"
            }
        }
       
        endpoint = "/tasks"

        response = self._client.post(endpoint, json=opgave_skabelon)
        response.raise_for_status()

        return response.json()