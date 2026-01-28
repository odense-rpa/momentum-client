from typing import Optional
from momentum_client.client import MomentumClient
from typing import Optional, List


class VirksomhederClient:
    def __init__(self, client: MomentumClient):
        self._client = client

    def hent_virksomheder(self, filters: List[dict], søgeterm: str = "*") -> Optional[dict]:
        """
        Hent virksomheder med angivne filtre og søgeterm.
        
        :param filters: Dictionary of filters to apply (optional)
        :param søgeterm: Search term to filter production units. Default is * ("alle")
        :param pagenumber: Page number for pagination. Default is 0
        :param pagesize: Number of items per page. Default is 1000
        :return: List of production units matching the criteria or None if not found
        """
        endpoint = "punits/searchproductionunits"
        sideindex = 0
        virksomheder = []
        has_more = True
        
        while has_more:
            # Klargør body
            body = {
                "paging": {
                    "pageNumber": sideindex,
                    "pageSize": 6000
                },
                
                "filters": filters,
                "term": søgeterm
            }
            
            response = self._client.post(endpoint, json=body)
            
            if response.status_code == 404:
                return None
            
            data = response.json()
            
            # Tilføj resultaterne til listen
            if data is not None:
                virksomheder.extend(data['data'])
            
            # Tjek om der er flere sider, sikkerhedstjek på mere end 110 sider
            if data['hasMore'] == False or sideindex > 110:
                has_more = False
            
            # Inkrementer sideindex for næste kald
            sideindex += 1
        
        return {'data': virksomheder}
    
    def hent_virksomheder_med_cvr(self, cvr: str) -> Optional[dict]:
        """
        Hent virksomhedser med angivet CVR-nummer.
        
        :param cvr: CVR-nummer for virksomheden
        :return: Company information or None if not found
        """
        endpoint = f"/companies/{cvr}"
        
        response = self._client.get(endpoint)
        
        if response.status_code == 404:
            return None
        
        return response.json()
    
    def hent_virksomhed_med_cvr_og_pnummer(self, cvr: str, pNummer: str) -> Optional[dict]:
        """
        Hent virksomhedsoplysninger på virksomhed der matcher angivet cvr og pnummer.
        
        :param cvr: CVR-nummer for virksomheden
        :return: Company information or None if not found
        """
        endpoint = f"/companies/{cvr}/productionunits/{pNummer}"
        
        response = self._client.get(endpoint)
        
        if response.status_code == 404:
            return None
        
        return response.json()
    
    def find_borgere_i_tilbud_på_virksomhed(self, virksomhedsid: str, filters: dict = None, søgeterm: str = ""):
        """
        Find borgere (citizens) in tilbud (offers/placements) at a specific virksomhed (company).
        
        :param virksomhedsid: Production unit ID for the company
        :param filters: List of filter dictionaries with fieldName, values, etc.
        :param søgeterm: Search term
        :return: Search results or None if not found
        """
        endpoint = f"/placements/productionUnit/{virksomhedsid}/search"
        
        # Prepare the request body according to the API model
        body = {
            "term": søgeterm or "",
            "filters": filters or [],
        }
        
        response = self._client.post(endpoint, json=body)
        
        if response.status_code == 404:
            return None
            
        return response.json()
    
    def find_jobordre_på_virksomhed(self, virksomhedsid: str, filters: dict = None, søgeterm: str = ""):
        """
        Find jobordre (job orders/recruitments) at a specific virksomhed (company).
        
        :param virksomhedsid: Production unit ID for the company
        :param filters: List of filter dictionaries with fieldName, values, etc.
        :param søgeterm: Search term
        :return: Search results or None if not found
        """
        endpoint = "/companyrecruitmentsearch"
        
        # Prepare the request body according to the API model
        request_filters = filters.copy() if filters else []
        
        # Add the required providerId filter
        provider_filter = {
            "values": [virksomhedsid],
            "fieldName": "providerId"
        }
        request_filters.append(provider_filter)
        
        body = {
            "term": søgeterm or "",
            "filters": request_filters
        }
        
        response = self._client.post(endpoint, json=body)
        
        if response.status_code == 404:
            return None
            
        return response.json()

    def søg_virksomhed_med_p_nummer(self, pnummer: str) -> Optional[dict]:
        """
        Hent virksomhedsoplysninger baseret på P-nummer.
        
        :param pnummer: P-nummer for virksomheden
        :return: Company information or None if not found
        """
        endpoint = f"/search"
        body = {"term": pnummer, 
                "size": 15, 
                "skip": 0, 
                "allowedCategories": 
                    ["Citizen", "Company", "ContactPerson", "Caseworker", "Offer", "JobOrder", "JobAd", "Course"], 
                "parentId": None,
                "isActive": True,
                "hasUserId": None,
                "isPhoneNumbersOnly": None,
                "includeInternalUsers": False
            }

        response = self._client.post(endpoint,
                                     json=body)
        
        if response.status_code == 404:
            return None

        return response.json()
    
    def hent_virksomheds_kontaktpersoner(self, virksomhedsId: str, søgeterm = "", sidetal_resultater: int = 1, antal_resultater: int = 999999, kun_active = True) -> Optional[dict]:
        """
        Hent kontaktpersoner for en given virksomhed baseret på virksomhedsId.
        
        :param virksomhedsId: ID for virksomheden
        :return: List of contact persons or None if not found
        """
        endpoint = f"/punits/{virksomhedsId}/contactpersons?&pageNumber={sidetal_resultater}&pageSize={antal_resultater}"
        body = {
            "searchText": søgeterm,
            "pageNumber": sidetal_resultater,
            "pageSize": antal_resultater,
            "onlyActive": kun_active
        }

        response = self._client.post(endpoint, json=body)

        if response.status_code == 404:
            return None
        
        return response.json()
    
    def hent_virksomheds_sagsbehandlere(self, virksomhedsId: str, søgeterm = "", sidetal_resultater: int = 1, antal_resultater: int = 999999, kun_active = True) -> Optional[dict]:
        """
        Hent sagsbehandlere for en given virksomhed baseret på virksomhedsId.
        
        :param virksomhedsId: ID for virksomheden
        :return: List of caseworkers or None if not found
        """
        endpoint = f"/punits/{virksomhedsId}/caseworkers?&pageNumber={sidetal_resultater}&pageSize={antal_resultater}"
        body = {
            "searchText": søgeterm,
            "pageNumber": sidetal_resultater,
            "pageSize": antal_resultater,
            "onlyActive": kun_active
        }

        response = self._client.post(endpoint, json=body)

        if response.status_code == 404:
            return None
        
        return response.json()
    
    def ændr_kontaktpersons_status(self, kontaktpersonId: str, status = False) -> bool:
        """
        Ændr status for en kontaktperson baseret på kontaktpersonId.

        :param kontaktpersonId: ID for kontaktpersonen
        :return: True if successful, False otherwise
        """
        endpoint = f"/employees/{kontaktpersonId}/status/{str(status).lower()}"

        response = self._client.post(endpoint)

        if response.status_code == 200:
            return True
        
        return False
    
    def hent_udvidet_virksomhedsinfo(self, virksomhedsId:str) -> Optional[dict]:
        endpoint = f"/punits/{virksomhedsId}"

        response = self._client.get(endpoint)

        if response.status_code == 404:
            return None

        return response.json()