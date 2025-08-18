import pytest
import os
from pathlib import Path

from dotenv import load_dotenv
from momentum_client.manager import MomentumClientManager

# Load environment variables from .env
load_dotenv()


@pytest.fixture(scope="session")
def momentum_manager():
    """Primary fixture - MomentumClientManager provides access to all functionality clients."""
    base_url = os.getenv("BASE_URL")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    api_key = os.getenv("API_KEY")
    resource = os.getenv("RESOURCE")

    if not all([base_url, client_id, client_secret, api_key, resource]):
        raise ValueError(
            "BASE_URL, CLIENT_ID, CLIENT_SECRET, API_KEY, and RESOURCE must be set in .env file"
        )

    return MomentumClientManager(
        base_url=base_url,
        client_id=client_id,
        client_secret=client_secret,
        api_key=api_key,
        resource=resource,
    )


@pytest.fixture(scope="session")
def base_client(momentum_manager):
    """Returns the underlying MomentumClient."""
    return momentum_manager._client


@pytest.fixture(scope="session")
def borgere_client(momentum_manager):
    """Returns the BorgereClient for citizen-related operations."""
    return momentum_manager._borgere_client


@pytest.fixture(scope="session")
def test_cpr():
    """Returns the test CPR from environment variables."""
    test_cpr = os.getenv("TEST_CPR")
    if not test_cpr:
        raise ValueError("TEST_CPR must be set in .env file")
    return test_cpr
