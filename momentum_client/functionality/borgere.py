from typing import Optional, List
import datetime
from enum import Enum
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
        
        borger = response.json()

        endpoint = f"citizens/{borger["citizenId"]}"
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
    
    def hent_markeringer(self, borger: dict) -> Optional[dict]:
        """
        Henter en borgers markeringer

        :param borger: Borgerens data som en Dict
        :return: Liste af markeringer som en Dict eller None hvis fejlet
        """
        endpoint = f"/tagassignments?referenceId={borger['id']}"
        response = self._client.get(endpoint)
        if response.status_code == 404:
            return None
        return response.json()

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
        
        endpoint = f"/tagassignments?referenceId={borger['id']}"
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
        formatted_slut_dato = slut_dato.strftime("%Y-%m-%dT22:00:00Z")

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
    
    def opret_notifikation(
        self,
        borger: dict,
        titel: str,
        start_dato: datetime.date,
        slut_dato: datetime.date,
        vigtighed_af_notifikation: str,
        beskrivelse: Optional[str] = None,
        synlig_i_header: bool = False
    ) -> Optional[dict]:
        """
        Create a notification for a citizen.

        :param borger: Citizen's data as a dictionary
        :param titel: Title of the notification
        :param start_dato: Start date of the notification
        :param slut_dato: End date of the notification
        :param vigtighed_af_notifikation: Importance level of the notification
        :param beskrivelse: Optional description of the notification
        :param synlig_i_header: Boolean flag indicating visibility in header
        :return: Created notification data as a dictionary or None if failed
        """
        godkendte_vigtigheder = {"info", "high", "low", "normal"}

        if vigtighed_af_notifikation not in godkendte_vigtigheder:
            raise ValueError(f"Ugyldig vigtighed: {vigtighed_af_notifikation}")

        body = {
            "referenceId": borger["citizenId"],
            "title": titel,
            "start": f"{start_dato}",
            "end": f"{slut_dato}",
            "alertSeverity": vigtighed_af_notifikation,
            "description": beskrivelse,
            "visibleInHeaderBar": synlig_i_header,
            "applicationContext" : 0,
            "attachmentIds": [
            ]
        }

        endpoint = f"/alerts"
        response = self._client.post(endpoint, json=body)
        return response.json() if response.status_code == 200 else None
    
    def opdater_borgers_ansvarlige_og_kontaktpersoner(
            self,
            borger: dict,
            medarbejderid: str,
            medarbejdertype: Optional[int] = 0,
            medarbejderrolle: str = "OVRIG_ANSVARLIG",
            privat_kontaktperson: bool = False
        ) -> Optional[dict]:
        """
        Opdaterer en borgers ansvarlige og kontaktpersoner.
        
        :param privat_kontaktperson: Flag som indikerer om det er en privat kontaktperson eller ej. Default er False.
        :param borger: Borgerens data som en Dict
        :param medarbejderid: Medarbejderens ID der skal påsættes borgeren

        :param medarbejdertype: Medarbejdertype er et tal, der giver typen:

            0 = Øvrige

            1 = Primære

        :param medarbejderrolle: Medarbejderrolle er den rolle der står i UI:

            "Øvrig ansvarlig": "OVRIG_ANSVARLIG",
            "Beskæftigelsessagsbehandler": "BESKAFTIGELSESSAGSBEHANDLER",
            "Anden aktør": "ANDEN_AKTOR",
            "Sanktionsteam": "74be96ca-5fd3-44c2-a951-cba7f3dc9c97",
            "Fastholdelseskonsulent": "CASEWORKER_RESPONSIBILITY_FASTHOLDELSESKONSULENT",
            "Jobkonsulent": "CASEWORKER_RESPONSIBILITY_JOBKONSULENT",
            "Kommunal udslusningskoordinator": "KOMMUNAL_UDSLUSNINGSKOORDINATOR",
            "Sekundær ansvarlig": "SEKUNDER_ANSVARLIG",
            "Leder": "LEDER",
            "Mentor": "MENTOR",
            "Personlig jobformidler": "PERSONLIG_JOBFORMIDLER",
            "Koordinerende sagsbehandler": "KOORDINERENDE_SAGSBEHANDLER",
            "Virksomhedskonsulent": "VIRKSOMHEDSKONSULENT",
            "Støtte-kontaktperson": "STØTTE-KONTAKTPERSON",
            "Ydelsesmedarbejder": "YDELSESMEDARBEJDER",
            "Tilbudsansvarlig": "TILBUDSANSVARLIG",
            "Uddannelsesvejleder": "UDDANNELSESVEJLEDER"

        pr 07/11/25 er listen opdateret - måske fuldent
        """

        if privat_kontaktperson == False:
            json_body = {
                "caseworkers": [
                    {
                    "actorId": f"{medarbejderid}",
                    "role": medarbejdertype,
                    "responsibilities": [
                        {
                        "responsibilityCode": f"{medarbejderrolle}",
                        "showInJobnet": None
                        }
                    ]
                    }
                ],
                "privateContactPersons": []
                }
        else:
            if medarbejderrolle == "Bisidder":
                private_responsibility_code = "0acce8a4-d610-4a97-9c57-5abd4d14ae80"
            elif medarbejderrolle == "Partsrepræsentant":
                private_responsibility_code = "fbe758a1-03aa-49c1-9ad5-27400b379cb7"
            elif medarbejderrolle == "Nexus-sagsbehandler":
                private_responsibility_code = "67e29cac-03b7-4386-8b2a-0e593b799b62"
            else:  # DUBU-sagsbehandler
                private_responsibility_code = "de7834a1-7739-4918-b251-ed67c001bb75"
            json_body = {
                "caseworkers": [],
                "privateContactPersons": [
                    {
                    "actorId": f"{medarbejderid}",
                    "responsibilityCodes": [f"{private_responsibility_code}"]
                    }
                ]
                }

        # hent alle borgers caseworkers:
        endpoint = f"/responsibleCaseworkers/all/byCitizen/{borger['id']}"
        alle_caseworkers_json = self._client.get(endpoint).json()
        # filtrer de aktive caseworkers
        active_caseworkers = [
            item for item in alle_caseworkers_json
            if item.get("endDate") is None
        ]

        # Process caseworkers using the logic from C# code
        # original_json is json_body, caseworker_json is active_caseworkers
        caseworkers = json_body.get("caseworkers", [])
        private_contacts = json_body.get("privateContactPersons", [])
        
        # Responsibility name to code mapping
        responsibility_mapping = {
            "Øvrig ansvarlig": "OVRIG_ANSVARLIG",
            "Beskæftigelsessagsbehandler": "BESKAFTIGELSESSAGSBEHANDLER",
            "Anden aktør": "ANDEN_AKTOR",
            "Sanktionsteam": "74be96ca-5fd3-44c2-a951-cba7f3dc9c97",
            "Fastholdelseskonsulent": "CASEWORKER_RESPONSIBILITY_FASTHOLDELSESKONSULENT",
            "Jobkonsulent": "CASEWORKER_RESPONSIBILITY_JOBKONSULENT",
            "Kommunal udslusningskoordinator": "KOMMUNAL_UDSLUSNINGSKOORDINATOR",
            "Sekundær ansvarlig": "SEKUNDER_ANSVARLIG",
            "Leder": "LEDER",
            "Mentor": "MENTOR",
            "Personlig jobformidler": "PERSONLIG_JOBFORMIDLER",
            "Koordinerende sagsbehandler": "KOORDINERENDE_SAGSBEHANDLER",
            "Virksomhedskonsulent": "VIRKSOMHEDSKONSULENT",
            "Støtte-kontaktperson": "STØTTE-KONTAKTPERSON",
            "Ydelsesmedarbejder": "YDELSESMEDARBEJDER",
            "Tilbudsansvarlig": "TILBUDSANSVARLIG",
            "Uddannelsesvejleder": "UDDANNELSESVEJLEDER"
        }
        
        for item in active_caseworkers:
            actor_id = str(item["caseworkerId"])
            responsibility_name = str(item["responsibilityName"])
            
            # Handle private contact persons separately
            if responsibility_name in ["Bisidder", "Partsrepræsentant", "DUBU-sagsbehandler", "Nexus-sagsbehandler"]:
                private_contact_id = str(item["id"])  # Use "id" instead of "caseworkerId"
                if responsibility_name == "Bisidder":
                    private_responsibility_code = "0acce8a4-d610-4a97-9c57-5abd4d14ae80"
                elif responsibility_name == "Partsrepræsentant":
                    private_responsibility_code = "fbe758a1-03aa-49c1-9ad5-27400b379cb7"
                elif responsibility_name == "Nexus-sagsbehandler":
                    private_responsibility_code = "67e29cac-03b7-4386-8b2a-0e593b799b62"
                else:  # DUBU-sagsbehandler
                    private_responsibility_code = "de7834a1-7739-4918-b251-ed67c001bb75"
                
                private_contact = {
                    "actorId": private_contact_id,
                    "responsibilityCodes": [private_responsibility_code]
                }
                
                private_contacts.append(private_contact)
                continue  # Skip the rest of the loop since it's not a caseworker
            
            # Parse role as a floating-point value
            role_value = float(item["role"])
            role = 1 if role_value == 1.0 else 0
            
            new_caseworker = {
                "actorId": actor_id,
                "role": role
            }
            
            # Map responsibilityName to responsibilityCode
            responsibility_code = responsibility_mapping.get(responsibility_name, "OVRIG_ANSVARLIG")
            
            # Safely parse "showInJobnet" without exceptions
            show_in_jobnet = (
                item.get("showInJobnet") is not None and 
                isinstance(item["showInJobnet"], bool) and 
                item["showInJobnet"]
            )
            
            if role == 0:  # When role is 0
                responsibility_obj = {
                    "responsibilityCode": responsibility_code
                }
                
                # Only add showInJobnet if it's true
                if show_in_jobnet:
                    responsibility_obj["showInJobnet"] = True
                else:
                    responsibility_obj["showInJobnet"] = None
                
                new_caseworker["responsibilities"] = [responsibility_obj]
            else:  # When role is 1
                new_caseworker["responsibilities"] = []  # Empty responsibilities
            
            caseworkers.append(new_caseworker)
        
        # Update json_body with processed data
        json_body["caseworkers"] = caseworkers
        json_body["privateContactPersons"] = private_contacts
        print(json_body)
        

        endpoint = f"/citizens/{borger['id']}/responsibleactors"
        response = self._client.put(endpoint, json=json_body)
        return response.json() if response.status_code == 200 else None
        
    def hent_sagsbehandler(self, initialer: str) -> Optional[dict]:
        """
        Hent sagsbehandler information baseret på medarbejderinitialer.

        :param initialer: Medarbejderens initialer
        :return: Sagsbehandler data som en Dict eller None hvis ikke fundet
        """
        
        medarbejdere = self._client.søg(søgeterm=initialer, kategori="Caseworker", kun_active=True, ønsket_antal=10)

        if not medarbejdere:
            return None

        # Description indeholder "initialer"@odense.dk og bruges til at finde den korrekte medarbejder:
        resultat = next((item for item in medarbejdere if item.get("description") == f"{initialer}@odense.dk"), None)
        return resultat
    
    def hent_ansvarlige_sagsbehandlere(self, borger: dict) -> Optional[List[dict]]:
        """
        Hent ansvarlige sagsbehandlere for en given borger.

        :param borger: Borgerens data som en Dict
        :return: Liste af ansvarlige sagsbehandlere som Dicts eller None hvis fejlet
        """
        endpoint = f"/responsibleCaseworkers/all/byCitizen/{borger['id']}"
        response = self._client.get(endpoint).json()
        if response is None:
            return None

        # behold kun aktive sagsbehandlere: caseworkerIsActive = 1, role = 1 og endDate = None
        aktive_sagsbehandlere = [
            item for item in response if item.get("caseworkerIsActive") == 1 and item.get("role") == 1 and item.get("endDate") is None
        ]
        return aktive_sagsbehandlere
    
    def hent_aktive_sagsbehandlere(self, borger: dict) -> Optional[List[dict]]:
        """
        Hent aktive sagsbehandlere for en given borger.

        :param borger: Borgerens data som en Dict
        :return: Liste af aktive sagsbehandlere som Dicts eller None hvis fejlet
        """
        endpoint = f"/responsibleCaseworkers/all/byCitizen/{borger['id']}"
        response = self._client.get(endpoint).json()
        if response is None:
            return None

        # behold kun aktive sagsbehandlere: caseworkerIsActive = 1 og endDate = None
        aktive_sagsbehandlere = [
            item for item in response if item.get("caseworkerIsActive") == 1 and item.get("endDate") is None
        ]
        return aktive_sagsbehandlere
    
    def hent_alle_private_kontaktpersoner(self, borger: dict) -> Optional[List[dict]]:
        """
        Hent alle private kontaktpersoner for en given borger.

        :param borger: Borgerens data som en Dict
        :return: Liste af private kontaktpersoner som Dicts eller None hvis fejlet
        """
        endpoint = f"/citizens/{borger['id']}/searchPrivateContacts"
        body = {"term":" ","paging":{"pageNumber":1,"pageSize":999}}
        response = self._client.post(endpoint, json=body).json()
        if response is None:
            return None

        return response
    
    def søg_specifik_privat_kontaktperson(self, borger: dict, søgeterm: str) -> Optional[dict]:
        """
        Hent en specifik privat kontaktperson for en given borger baseret på søgeterm.

        :param borger: Borgerens data som en Dict
        :param søgeterm: Søgeterm for kontaktpersonen
        :return: Kontaktperson data som en Dict eller None hvis ikke fundet
        """
        endpoint = f"/citizens/{borger['id']}/searchPrivateContacts"
        body = {"term": søgeterm, "paging": {"pageNumber": 1, "pageSize": 10}}
        response = self._client.post(endpoint, json=body).json()
        if response is None:
            return None

        return response
    
    def hent_specifik_privat_kontaktperson(self, borger: dict, kontaktperson_id: str) -> Optional[dict]:
        """
        Hent en specifik privat kontaktperson for en given borger baseret på kontaktperson ID.

        :param borger: Borgerens data som en Dict
        :param kontaktperson_id: Kontaktpersonens ID
        :return: Kontaktperson data som en Dict eller None hvis ikke fundet
        """
        endpoint = f"/citizens/{borger['id']}/privateContacts/{kontaktperson_id}"
        response = self._client.get(endpoint)
        if response.status_code == 404:
            return None
        return response.json()

    def hent_aktør(self, aktør_id: str) -> Optional[dict]:
        """
        Hent aktør information baseret på aktør ID.
        Aktør ID kan findes ved at bruge hent_sagsbehandler metoden.

        :param aktør_id: Aktørens ID
        :return: Aktør data som en Dict eller None hvis ikke fundet
        """
        endpoint = f"/actors/{aktør_id}/details"
        response = self._client.get(endpoint)
        if response.status_code == 404:
            return None
        return response.json()
    
    def opret_privat_kontaktpersoner(self, borger: dict,
                                     titel: str, navn: str, email: str, telefon: str) -> Optional[dict]:
        """
        Opret en privat kontaktperson for en given borger.

        :param borger: Borgerens data som en Dict
        :param titel: Titel på kontaktpersonen
        :param navn: Navn på kontaktpersonen
        :param email: Email på kontaktpersonen
        :param telefon: Telefonnummer på kontaktpersonen
        :return: Oprettet kontaktperson data som en Dict eller None hvis fejlet
        """
        endpoint = f"/citizens/{borger['id']}/privateContacts"
        json_body = {
            "email": {"email": email},
            "mobile": {"number": telefon, "isMobile": True},
            "phone": {"number": "", "isMobile": False},
            "address": {
                "street": "",
                "building": "",
                "suite": "",
                "postalCode": "",
                "city": "",
                "countryCode": None,
                "start": None,
                "end": None
            },
            "description": "",
            "title": titel,
            "isActive": False,
            "cpr": "",
            "name": navn,
            "citizenId": borger['id']
        }
        response = self._client.post(endpoint, json=json_body)
        return response.json() if response.status_code == 200 else None
    
    def _strukturér_privat_kontaktperson_data(self, kontaktperson_json: dict, borger: dict) -> dict:
        """
        Strukturer privat kontaktperson data til det korrekte format for API opdatering.
        
        :param kontaktperson_json: Den rå kontaktperson data fra API'et
        :param borger: Borgerens data som en Dict
        :return: Struktureret kontaktperson data klar til API opdatering
        """
        # Sørg for at vi har de nødvendige felter med fallback værdier
        structured_data = {
            "email": {
                "email": kontaktperson_json.get('email', {}).get('address', '') if isinstance(kontaktperson_json.get('email'), dict) else ""
            },
            "mobile": {
                "number": kontaktperson_json.get('mobile', {}).get('number', '') if isinstance(kontaktperson_json.get('mobile'), dict) else "",
                "isMobile": True
            },
            "phone": {
                "number": kontaktperson_json.get('phone', {}).get('number', '') if isinstance(kontaktperson_json.get('phone'), dict) else "",
                "isMobile": False
            },
            "address": {
                "street": kontaktperson_json.get('address', {}).get('street', '') if isinstance(kontaktperson_json.get('address'), dict) else "",
                "building": kontaktperson_json.get('address', {}).get('building', '') if isinstance(kontaktperson_json.get('address'), dict) else "",
                "suite": kontaktperson_json.get('address', {}).get('suite', '') if isinstance(kontaktperson_json.get('address'), dict) else "",
                "postalCode": kontaktperson_json.get('address', {}).get('postalCode', '') if isinstance(kontaktperson_json.get('address'), dict) else "",
                "city": kontaktperson_json.get('address', {}).get('city', '') if isinstance(kontaktperson_json.get('address'), dict) else "",
                "countryCode": kontaktperson_json.get('address', {}).get('countryCode') if isinstance(kontaktperson_json.get('address'), dict) else None,
                "start": kontaktperson_json.get('address', {}).get('start') if isinstance(kontaktperson_json.get('address'), dict) else None,
                "end": kontaktperson_json.get('address', {}).get('end') if isinstance(kontaktperson_json.get('address'), dict) else None
            },
            "description": kontaktperson_json.get('description', ''),
            "title": kontaktperson_json.get('title', ''),
            "isActive": kontaktperson_json.get('isActive', False),
            "cpr": kontaktperson_json.get('cpr', ''),
            "id": kontaktperson_json.get('id', ''),
            "name": kontaktperson_json.get('name', kontaktperson_json.get('displayName', '')),
            "citizenId": borger['id']
        }
        
        return structured_data
    
    def inaktiver_privat_kontaktperson(self, borger: dict, kontaktperson_navn: str) -> bool:
        """
        Inaktiver en privat kontaktperson for en given borger.

        :param borger: Borgerens data som en Dict
        :param kontaktperson_navn: Navnet på den private kontaktperson der skal inaktiveres
        :return: True hvis inaktivering lykkedes, ellers False
        """
        kontaktperson_data = self.søg_specifik_privat_kontaktperson(borger, kontaktperson_navn)
        kontaktperson_json = self.hent_specifik_privat_kontaktperson(borger, kontaktperson_data["data"][0]['id'])
        if kontaktperson_json is None:
            return False
        
        # Strukturer data til korrekt format
        structured_data = self._strukturér_privat_kontaktperson_data(kontaktperson_json, borger)
        structured_data['isActive'] = False  # Sæt til inaktiv
        
        endpoint = f"/citizens/{borger['id']}/privateContacts/{structured_data['id']}"
        response = self._client.put(endpoint, json=structured_data)
        return response.status_code == 200
    
    def fjern_ansvarlig_eller_privat_kontaktperson(self, borger: dict, sagsbehandler_navn: str) -> bool:
        """
        Fjern en ansvarlig sagsbehandler eller privat kontaktperson fra en given borger.

        :param borger: Borgerens data som en Dict
        :param sagsbehandler_navn: Sagsbehandlerens navn der skal fjernes
        :return: True hvis fjernelse lykkedes, ellers False
        """
        json_body = {
            "caseworkers": [],
            "privateContactPersons": []
        }
        
        # henter alle borgers aktive sagsbehandlere og private kontaktpersoner med tilhørende JSON
        endpoint_body = {
            "columns": ["name", "type", "responsibilityTypeCode", "startDate", "endDate",],
            "paging": {"pageNumber": 0, "pageSize": 50},
            "sort": [
                {"fieldName": "sortableEndDate", "ascending": False},
                {"fieldName": "startDate", "ascending": False}
            ],
            "filters": [
                {
                    "fieldName" : "endDate",
                    "values" : [
                       None, None, True
                    ],
                }
            ],
            "searchFieldsDetails": [],
            "impersonateCaseworkerId": None,
            "term": ""
        }
        alle_borgers_sagsbehandlere_og_private_kontaktpersoner = self._client.post(f"/citizens/{borger['id']}/searchContacts", json=endpoint_body).json()

        # fjern sagsbehandler eller privat kontaktperson baseret på navn:
        


        # hvis sagsbehandler["type"] == 2, så er det en private. Ellers er det en caseworker:
        for item in alle_borgers_sagsbehandlere_og_private_kontaktpersoner["data"]:
            # Skip personen der skal fjernes
            if item.get("name", "").lower().strip() == sagsbehandler_navn.lower().strip():
                continue  # Spring denne person over - den bliver ikke tilføjet til json_body
            if item.get("type") == 2:  # Privat kontaktperson
                json_body["privateContactPersons"].append({
                    "actorId": str(item.get("actorId")),
                    "responsibilityCodes": [item.get("responsibilityTypeCode")]
                })
            else:  # Sagsbehandler
                # Determine responsibilities based on type
                if item.get("type") == 1:
                    responsibilities = []
                else:
                    responsibilities = [
                        {
                            "responsibilityCode": item.get("responsibilityTypeCode"),
                            "showInJobnet": None
                        }
                    ]
                
                json_body["caseworkers"].append({
                    "actorId": str(item.get("actorId")),
                    "role": 1 if float(item.get("type", 0)) == 1.0 else 0,
                    "responsibilities": responsibilities
                })

        # alle_borgers_sagsbehandlere_og_private_kontaktpersoner = self.hent_aktive_sagsbehandlere(borger)

        endpoint = f"/citizens/{borger['id']}/responsibleactors"
        response = self._client.put(endpoint, json=json_body)
        return response.status_code == 200