from typing import Optional
import datetime
from momentum_client.client import MomentumClient


class VirksomhederClient:
    def __init__(self, client: MomentumClient):
        self._client = client

    def hent_virksomheder(self, filters: dict = None, søgeterm: str = "*", sidetal_resultater: int = 0, antal_resultater: int = 1000) -> Optional[dict]:
        """
        Hent virksomheder med angivne filtre og søgeterm.
        
        :param filters: Dictionary of filters to apply (optional)
        :param søgeterm: Search term to filter production units. Default is * ("alle")
        :param pagenumber: Page number for pagination. Default is 0
        :param pagesize: Number of items per page. Default is 1000
        :return: List of production units matching the criteria or None if not found
        """
        endpoint = "punits/searchproductionunits"
        
        # Prepare the request body
        body = {
            "søgeterm": søgeterm,
            "paging": {
                "pageNumber": sidetal_resultater,
                "pageSize": antal_resultater
            }
        }
        
        # Add filters if provided
        if filters:
            body["filters"] = filters
        
        response = self._client.post(endpoint, json=body)
        
        if response.status_code == 404:
            return None
        
        return response.json()
    
    def hent_virksomheder_med_cvr(self, cvr: str) -> Optional[dict]:
        """
        Hent virksomhedsoplysninger baseret på CVR-nummer.
        
        :param cvr: CVR-nummer for virksomheden
        :return: Company information or None if not found
        """
        endpoint = f"/companies/{cvr}"
        
        response = self._client.get(endpoint)
        
        if response.status_code == 404:
            return None
        
        return response.json()
    
    def find_borgere_i_tilbud_på_virksomhed(self, virksomhed:dict, filters: dict = None, søgeterm: str = ""):
        """
        Find borgere (citizens) in tilbud (offers/placements) at a specific virksomhed (company).
        
        :param virksomhed: Dictionary containing company information with productionUnitId
        :param filters: List of filter dictionaries with fieldName, values, etc.
        :param søgeterm: Search term
        :return: Search results or None if not found
        """
        endpoint = f"/placements/productionUnit/{virksomhed["productionUnitId"]}/search"
        
        # Prepare the request body according to the API model
        body = {
            "term": søgeterm or "",
            "filters": filters or [],
        }
        
        response = self._client.post(endpoint, json=body)
        
        if response.status_code == 404:
            return None
            
        return response.json()
    
    def find_jobordre_på_virksomhed(self, virksomhed: dict, filters: dict = None, søgeterm: str = ""):
        """
        Find jobordre (job orders/recruitments) at a specific virksomhed (company).
        
        :param virksomhed: Dictionary containing company information with productionUnitId
        :param filters: List of filter dictionaries with fieldName, values, etc.
        :param søgeterm: Search term
        :return: Search results or None if not found
        """
        endpoint = "/companyrecruitmentsearch"
        
        # Prepare the request body according to the API model
        request_filters = filters.copy() if filters else []
        
        # Add the required providerId filter
        provider_filter = {
            "values": [virksomhed['productionUnitId']],
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

