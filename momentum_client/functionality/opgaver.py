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

    def opret_opgave(self, borger: dict, medarbejdere: list[dict], forfaldsdato: datetime, titel: str, beskrivelse: str, borger_opgave: bool = True) -> dict:
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
                "type": "CITIZEN" if borger_opgave else "PRODUCTIONUNIT"
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
    
    def hent_opgaver_på_virksomhed(self, virksomhedsid:str) -> list[dict] | None:
        
        opgave_liste = []
        antal_hentet_opgaver = 150
        side_nummer = 0
        endpoint = "/tasks/company"
        flere_sider = True

        while flere_sider:
            json_skabelon = {
                "columns": [],
                "filters": [
                    {
                        "fieldName": "productionUnitId",
                        "values": [virksomhedsid]
                    }
                ],
                "sort": [
                    {
                        "fieldName": "deadline",
                        "ascending": True
                    }
                ],
                "paging": {
                    "pageNumber": side_nummer,
                    "pageSize": antal_hentet_opgaver
                }
            }

            response = self._client.post(endpoint, json=json_skabelon)
                
            if response.status_code == 404:
                return None
            
            data = response.json()

            if data is not None:
                opgave_liste.extend(data['data'])
                
            # Tjek om der er flere sider
            if len(opgave_liste) >= data['totalSearchCount'] or side_nummer > 20:
                flere_sider = False
            
            side_nummer += 1
        
        return opgave_liste
    
    def opdater_opgave_status(self, opgaveid: str, status: Status) -> dict:
        """Ændre status på en opgave."""
        endpoint = f"tasks/{opgaveid}/{status.value}"

        response = self._client.put(endpoint)

        if response.status_code == 400:
            raise Exception("Fejl, kunne ikke ændre status")
        
        return response.json()
    
    def søg_borger_opgaver(self, søge_filtre: dict, side_størrelse: int = 100) -> list[dict]:
        """
        Søg efter opgaver for en given borger.

        :param søge_filtre: Dictionary med filtre for søgningen
        :param side_størrelse: Antal opgaver pr. side
        :return: Liste af opgaver som dictionaries
        """
        sidenummer = 0        
        endpoint = "/tasks/citizen"
        samlede_opgaver = []

        while True:
            response = self._client.post(endpoint, json=søge_filtre)
            response.raise_for_status()

            if response.status_code != 200:
                break

            payload = response.json()
            samlede_opgaver.extend(payload.get("data", []))

            total_search_count = payload.get("totalSearchCount", len(samlede_opgaver))
            if total_search_count <= side_størrelse * (sidenummer + 1):
                break

            sidenummer += 1
            søge_filtre["paging"]["pageNumber"] = sidenummer

        return samlede_opgaver