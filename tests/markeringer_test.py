# Fixtures are automatically loaded from conftest.py

import datetime
import pytest
from momentum_client.manager import MomentumClientManager

def test_hent_markering_default(momentum_manager: MomentumClientManager):
    """Test hent_markering with default markeringsnavn."""
    response = momentum_manager.markeringer.hent_markering()
    assert response is not None
    assert response.get("title") == "ØF-JC-AC-IT-emnebank"

def test_hent_markering_custom(momentum_manager: MomentumClientManager):
    """Test hent_markering med en custom markeringsnavn."""
    # Using a different marking name that should exist
    response = momentum_manager.markeringer.hent_markering("TEST - RPA TYRA ROBOT - TEST - VIRKSOMHED")
    assert response is not None
    assert response.get("title") == "TEST - RPA TYRA ROBOT - TEST - VIRKSOMHED"

def test_hent_markeringer_med_reference_id(momentum_manager: MomentumClientManager, test_virksomhedsid):
    """Test hent_markeringer with a valid reference ID."""
    # Using a test reference ID - you may need to adjust this based on your test data
    reference_id = test_virksomhedsid
    response = momentum_manager.markeringer.hent_markeringer(reference_id)
    # Response can be None if no markings exist for this reference ID, which is acceptable
    assert response is None or isinstance(response, list)

def test_opret_og_slet_markering(momentum_manager: MomentumClientManager, test_virksomhedsid):
    """Test opret_markering with valid data."""
    markeringsnavn = "TEST - RPA TYRA ROBOT - TEST - VIRKSOMHED"
    reference_id = test_virksomhedsid
    start_dato = datetime.date.today()
    
    # First check if the marking exists
    markering = momentum_manager.markeringer.hent_markering(markeringsnavn)
    if markering is None:
        # Skip test if marking doesn't exist
        pytest.skip(f"Marking '{markeringsnavn}' not found")
    
    response = momentum_manager.markeringer.opret_markering(
        markeringsnavn=markeringsnavn,
        referenceId=reference_id,
        start_dato=start_dato
    )
    assert response["tag"]["title"] == markeringsnavn

    slettet_markering = momentum_manager.markeringer.slet_markering(response["id"])
    assert slettet_markering is True

def test_opret_og_afslut_markering(momentum_manager: MomentumClientManager, test_cpr):
    """Test af opret og afslut_markering """
    # Mock marking data structure
    markeringsnavn = "TEST - RPA TYRA ROBOT - TEST - BORGER"
    
    start_dato = datetime.date.today() + datetime.timedelta(days=2)
    
    borger = momentum_manager.borgere.hent_borger(test_cpr)
    slut_dato = datetime.datetime.today()

    response = momentum_manager.markeringer.opret_markering(
        markeringsnavn=markeringsnavn,
        referenceId=borger["citizenId"],
        start_dato=start_dato
    )
    assert response["tag"]["title"] == markeringsnavn
    slut_dato = datetime.date.today() + datetime.timedelta(days=5)
    
    response = momentum_manager.markeringer.afslut_markering(response, slut_dato)
    # Response might be None if update fails, which is acceptable for test data
    assert response["tag"]["title"] == markeringsnavn
    
    # Tjekker at enddate er sat til slut_dato
    end_date = datetime.datetime.fromisoformat(response["end"]).date()
    assert end_date == slut_dato