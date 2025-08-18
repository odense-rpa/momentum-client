import datetime
import os

from dotenv import load_dotenv
from momentum_client.manager import MomentumClientManager

load_dotenv()

def test_hent_borger():
    base_url = os.getenv("BASE_URL")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    api_key = os.getenv("API_KEY")
    resource = os.getenv("RESOURCE")

    client = MomentumClientManager(
        base_url = base_url,
        client_id = client_id,
        client_secret = client_secret,
        api_key = api_key,
        resource = resource
    )

    # Test with a valid TEST CPR number
    response = client._borgere_client.hent_borger("")
    assert response is not None    

def test_hent_borgere():
    base_url = os.getenv("BASE_URL")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    api_key = os.getenv("API_KEY")
    resource = os.getenv("RESOURCE")

    client = MomentumClientManager(
        base_url = base_url,
        client_id = client_id,
        client_secret = client_secret,
        api_key = api_key,
        resource = resource
    )

    filters = [
        {
            "customFilter": "",
            "fieldName": "targetGroupCode",
            "values": [
                "6.6",
            ]
        },
    ]
    response = client._borgere_client.hent_borgere(filters)
    assert response is not None

# Test hent_markering med default markeringsnavn
def test_hent_markering():
    base_url = os.getenv("BASE_URL")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    api_key = os.getenv("API_KEY")
    resource = os.getenv("RESOURCE")

    client = MomentumClientManager(
        base_url = base_url,
        client_id = client_id,
        client_secret = client_secret,
        api_key = api_key,
        resource = resource
    )

    response = client._borgere_client.hent_markering()
    assert response is not None

# Test hent_markering med et specifikt markeringsnavn
def test_hent_markering_specific():
    base_url = os.getenv("BASE_URL")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    api_key = os.getenv("API_KEY")
    resource = os.getenv("RESOURCE")

    client = MomentumClientManager(
        base_url = base_url,
        client_id = client_id,
        client_secret = client_secret,
        api_key = api_key,
        resource = resource
    )
    response = client._borgere_client.hent_markering("1. fællessamtale i jobcentret gennemført")
    assert response is not None
    assert response.get("title") == "1. fællessamtale i jobcentret gennemført"

def test_opret_markering():
    base_url = os.getenv("BASE_URL")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    api_key = os.getenv("API_KEY")
    resource = os.getenv("RESOURCE")

    client = MomentumClientManager(
        base_url = base_url,
        client_id = client_id,
        client_secret = client_secret,
        api_key = api_key,
        resource = resource
    )

    # Test opret_markering med en gyldig markering
    markeringsnavn = "Teknisk forlængelse - sygedagpenge"
    # IKKE COMMIT CPR-nummer i test
    borger = client._borgere_client.hent_borger("")
    start_dato = datetime.date.today()

    response = client._borgere_client.opret_markering(markeringsnavn, borger, start_dato)
    assert response is not None

    slettet_markering = client._borgere_client.slet_markering(response["id"])
    assert slettet_markering is True

def test_afslut_markering():
    base_url = os.getenv("BASE_URL")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    api_key = os.getenv("API_KEY")
    resource = os.getenv("RESOURCE")

    client = MomentumClientManager(
        base_url = base_url,
        client_id = client_id,
        client_secret = client_secret,
        api_key = api_key,
        resource = resource
    )
    # IKKE COMMIT CPR-nummer i test
    borger = client._borgere_client.hent_borger("")
    borgers_markeringer = client._borgere_client.hent_markeringer(borger)
    slut_dato = datetime.datetime.today()

    test_markering = next((markering for markering in borgers_markeringer if markering['tag']['title'] == "Teknisk forlængelse - sygedagpenge" and markering['end'] is None), None)
    assert test_markering is not None

    afsluttet_markering = client._borgere_client.afslut_markering(test_markering, slut_dato)
    assert afsluttet_markering is not None

def test_opret_notifikation():
    base_url = os.getenv("BASE_URL")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    api_key = os.getenv("API_KEY")
    resource = os.getenv("RESOURCE")

    client = MomentumClientManager(
        base_url = base_url,
        client_id = client_id,
        client_secret = client_secret,
        api_key = api_key,
        resource = resource
    )

    # IKKE COMMIT CPR-nummer i test
    borger = client._borgere_client.hent_borger("")
    start_dato = datetime.date.today()
    slut_dato = start_dato + datetime.timedelta(days=7)

    response = client._borgere_client.opret_notifikation(
        borger=borger,
        titel="Test Notifikation",
        start_dato=start_dato,
        slut_dato=slut_dato,
        vigtighed_af_notifikation="info",
        beskrivelse="Dette er en testnotifikation.2222",
        synlig_i_header=True
    )
    assert response is not None