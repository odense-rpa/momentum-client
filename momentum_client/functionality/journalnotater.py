from datetime import datetime
from typing import Optional

from momentum_client.client import MomentumClient


class JournalnotaterClient:
    def __init__(self, client: MomentumClient):
        self._client = client

    def hent_journalnotater(self, referenceid: str) -> Optional[dict]:
        endpoint = f"/journals/{referenceid}"
        response = self._client.get(endpoint)

        return response.json()

    def opret_journalnotat(
        self,
        borger: dict,
        sag: dict,
        hændelsesdato: datetime,
        titel: str,
        tekst: str,
        journaltype: str,
        kle_nummer: str,
        handlingsfacet: str,
    ) -> dict:
        journaltyper = {
            "fb60c76f-d4b2-44c2-b297-70912a7fbb9c": "Fremmøderapport",
            "b5e8e093-c31d-40f1-93e5-4e488a72f904": "Sagshændelse",
            "582FB102-548F-EE11-827B-00155DDBB303": "A-kasseunderretning",
            "44654224-4BC5-E311-8456-00155D177806": "Resultatbaseret styring",
            "3805612F-AFAA-4955-8865-E9A922B20567": "Besked fra a-kasse",
        }

        journaltype_id = next(
            (key for key, value in journaltyper.items() if value == journaltype),
            None,
        )

        if journaltype_id is None:
            raise ValueError(
                f"Ugyldig journaltype: {journaltype}. Gyldige journaltyper er: {', '.join(journaltyper.values())}"
            )

        # journaltype_id = "022.405.000" Testing purposes

        skabelon = {
            "createdAt": "1970-01-01T00:00:00.000Z",
            "updatedAt": "1970-01-01T00:00:00.000Z",
            "title": titel,
            "referenceId": borger["id"],
            "occurredAt": hændelsesdato.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "body": tekst,
            "attachments": [],
            "journalTypeId": journaltype_id,
            "isApproved": True,
            "caseId": sag["id"],
            "caseTagCode": f"KLE_{kle_nummer}",
            "caseActionFacetTagCode": f"KLE_ACTION_FACETS_{handlingsfacet}",
        }

        endpoint = "/journals/note"
        response = self._client.post(endpoint, json=skabelon)
        return response.json()
