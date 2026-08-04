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

    def _oversæt_hændelsestype_til_kode(self, borger: dict, hændelsestype: str) -> Optional[str]:
            # Fetch målgrupper for the citizen.
            målgrupper = self.hent_målgrupper(borger)
            if målgrupper is None:
                raise ValueError("Ingen målgrupper fundet for borgeren.")
    
            målgruppe_liste = self._to_list(målgrupper)
            aktive_målgrupper = [
                målgruppe
                for målgruppe in målgruppe_liste
                if isinstance(målgruppe, dict) and målgruppe.get("end") == "01-01-0001"
            ]
            if not aktive_målgrupper:
                raise ValueError("Ingen aktiv målgruppe fundet for borgeren.")
    
            aktiv_målgruppe = aktive_målgrupper[0]
            målgruppe_kode = self._first_present(aktiv_målgruppe, ["targetGroupCode"])
            if målgruppe_kode == "6.6":
                return "ABSENCE_CAUSE_TYPE"
    
            # Else fetch "taxonomies/SANCTION_CAUSE_EVENT_TYPES".
            taxonomi_svar = self._client.get("/taxonomies/SANCTION_CAUSE_EVENT_TYPES").json()
            taksonomi_værdier = self._to_list(
                taxonomi_svar.get("taxons", taxonomi_svar) if isinstance(taxonomi_svar, dict) else taxonomi_svar
            )
    
            taksonomi_kode = None
            for værdi in taksonomi_værdier:
                if not isinstance(værdi, dict):
                    continue
                if værdi.get("name") == hændelsestype:
                    taksonomi_kode = værdi.get("code")
                    if taksonomi_kode:
                        break
    
            # Fetch allowed values "/rules/" & [Borger.id].
            regler = self._client.get(f"/rules/{borger['id']}").json()
            tilladte_koder = []
            if isinstance(regler, dict):
                availability = regler.get("availability")
                if isinstance(availability, dict):
                    tilladte_koder = self._to_list(availability.get("allowedSanctionCauseEventTypeCodes"))
    
            # Loop [Regler.availability.allowedSanctionCauseEventTypeCodes] and check against the taxonomy code.
            if taksonomi_kode and (not tilladte_koder or taksonomi_kode in tilladte_koder):
                return taksonomi_kode
    
            return None