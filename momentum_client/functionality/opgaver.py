from datetime import datetime
from enum import Enum
from momentum_client.client import MomentumClient


class OpgaverClient:
    class Status(Enum):
        """Status værdier for opgaver i Momentum."""
        gennemført = 0
        aflyst = 1
        igang = 3
    
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
    
    def hent_opgaver(self, borger: dict) -> list[dict]:
        """
        Hent alle opgaver for en given borger.

        :param borger: Borger objekt eller ID
        :return: Liste af opgaver som dictionaries
        """
        antal_hentet_opgaver = 150
        alle_opgaver = []
        page_number = 0
        borgers_totale_antal_opgaver = 0

        while len(alle_opgaver) < borgers_totale_antal_opgaver or page_number == 0:
            json_skabelon = {
                "columns": [],
                "filters": [
                    {
                        "fieldName": "citizenId",
                        "values": [f"{borger['id']}" if isinstance(borger, dict) else f"{borger}"]
                    }
                ],
                "sort": [
                    {
                        "fieldName": "deadline",
                        "ascending": True
                    }
                ],
                "paging": {
                    "pageNumber": page_number,
                    "pageSize": antal_hentet_opgaver
                }
            }

            endpoint = "/tasks/citizen"
            response = self._client.post(endpoint, json=json_skabelon)
            response.raise_for_status()
            opgaver = response.json()
            
            alle_opgaver.extend(opgaver.get("data", []))
            borgers_totale_antal_opgaver = opgaver.get("totalSearchCount", 0)
            
            page_number += 1

        return alle_opgaver
    
    def opdater_opgave_status(self, opgaveid: str, status: Status) -> dict:
        """Ændre status på en opgave."""
        endpoint = f"tasks/{opgaveid}/{status.value}"

        response = self._client.put(endpoint)

        if response.status_code == 400:
            raise Exception("Fejl, kunne ikke ændre status")
        
        return response.json()