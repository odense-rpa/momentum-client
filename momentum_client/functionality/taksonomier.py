from typing import List, Optional
from momentum_client.client import MomentumClient

class TaksonomierClient:
    def __init__(self, client: MomentumClient):
        self._client = client
    
    def hent_alle_taksonomier(self) -> dict:
        """
        Hent alle taksonomigrupper.

        :return: Alle taksonomigrupper som en Dict
        """
        endpoint = f"/taxonomies"

        response = self._client.get(endpoint)

        return response.json()


    def find_taksonomi_gruppe(self, taksonomi_kode:str) -> Optional[dict]:
        """
        Find en taksonomigruppe ud fra dens kode.

        :param taksonomi_kode: Koden for taksonomigruppen
        :return: Taksonomigruppen som en Dict eller None hvis ikke fundet
        """
        endpoint = f"/taxonomies/{taksonomi_kode}"

        response = self._client.get(endpoint)

        if response.status_code == 404:
            return None
        
        return response.json()


    def find_taksonomi_kode(self, taksonomi_navn: str, kode_gruppe: Optional[str] = None) -> Optional[str]:
        """
        Find taksonomikoden for et givent taksonominavn.

        :param taksonomi_navn: Navnet på taksonomien der skal findes en kode for
        :param kode_gruppe: Begræns søgningen til taksonomigruppen med denne kode
        :return: Taksonomikoden eller None hvis der ikke findes præcis ét match
        """
        taksonomier = self.hent_alle_taksonomier()

        koder = []

        for taksonomi in taksonomier:
            if kode_gruppe is not None and taksonomi["code"] != kode_gruppe:
                continue
            for item in taksonomi .get("items", []):
                if item.get("name") == taksonomi_navn:
                    koder.append({
                        "taxonomy_code": item["code"],
                    })

        if len(koder) == 1:
            return koder[0]["taxonomy_code"]
        else:
            return None
    