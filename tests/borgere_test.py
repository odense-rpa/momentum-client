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