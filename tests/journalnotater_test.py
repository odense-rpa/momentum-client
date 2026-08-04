# Fixtures are automatically loaded from conftest.py

from datetime import datetime, timezone

from momentum_client.manager import MomentumClientManager


def test_hent_journalnotater(momentum_manager: MomentumClientManager, test_virksomhedsid):
    """Test hent_journalnotater with a valid reference ID."""
    reference_id = "0000c9d7-8e5e-462e-8e53-54afe4bbec32"
    response = momentum_manager.journalnotater.hent_journalnotater(reference_id)
    assert response is not None
    assert isinstance(response, (dict, list))

def test_opret_journalnotat(momentum_manager: MomentumClientManager, test_cpr):    
    borger = momentum_manager.borgere.hent_borger(test_cpr)
    assert borger is not None

    sager = momentum_manager.borgere.hent_sager(borger)
    assert sager is not None
    sag = sager[0]
    
    response = momentum_manager.journalnotater.opret_journalnotat(
        borger=borger,
        sag=sag,
        hændelsesdato=datetime.now(timezone.utc),
        titel="Test journalnotat",
        tekst="Automatisk test-oprettet journalnotat",
        journaltype="Sagshændelse",
        kle_nummer="15.17.06",
        handlingsfacet="G01",
    )

    assert response is not None
    assert isinstance(response, dict)