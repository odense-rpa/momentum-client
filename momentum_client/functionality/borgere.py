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
        endpoint = f"/tagassignments?referenceId={borger['citizenId']}"
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
            medarbejdertype = 0,
            medarbejderrolle: str = "OVRIG_ANSVARLIG"
        ) -> Optional[dict]:
        """
        Opdaterer en borgers ansvarlige og kontaktpersoner.
        Medarbejdertype er et tal, der giver typen:
        * 0 = Øvrige
        * 1 = Primære

        -----
        Medarbejderrolle er den rolle der står i UI:

        * OVRIG_ANSVARLIG = Øvrig Ansvarlig
        * BESKAFTIGELSESSAGSBEHANDLER = Beskæftigelsessagsbehandler

        pr 12/12/24 er listen opdateret - ikke fuldent
        """

        json_body = {
            "caseworkers": [
                {
                "actorId": f"{medarbejderid}",
                "role": f"{medarbejdertype}",
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

        # hent alle borgers caseworkers:
        endpoint = f"/responsibleCaseworkers/all/byCitizen/{borger['citizenId']}"
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
            if responsibility_name in ["Bisidder", "Partsrepræsentant"]:
                private_contact_id = str(item["id"])  # Use "id" instead of "caseworkerId"
                private_responsibility_code = (
                    "0acce8a4-d610-4a97-9c57-5abd4d14ae80" if responsibility_name == "Bisidder"
                    else "fbe758a1-03aa-49c1-9ad5-27400b379cb7"
                )
                
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

        endpoint = f"/citizens/{borger['citizenId']}/responsibleactors"
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
        response = self._client.get(endpoint)
        if response.status_code == 404:
            return None

        # behold kun aktive sagsbehandlere: caseworkerIsActive = 1, role = 1 og endDate = None
        aktive_sagsbehandlere = [
            item for item in response.json() if item.get("caseworkerIsActive") == 1 and item.get("role") == 1 and item.get("endDate") is None
        ]
        return aktive_sagsbehandlere

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