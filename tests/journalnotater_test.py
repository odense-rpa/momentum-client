# Fixtures are automatically loaded from conftest.py

from momentum_client.manager import MomentumClientManager


def test_hent_journalnotater(momentum_manager: MomentumClientManager, test_virksomhedsid):
    """Test hent_journalnotater with a valid reference ID."""
    reference_id = "0000c9d7-8e5e-462e-8e53-54afe4bbec32"
    response = momentum_manager.journalnotater.hent_journalnotater(reference_id)
    assert response is not None
    assert isinstance(response, (dict, list))
