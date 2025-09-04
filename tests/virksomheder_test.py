# Fixtures are automatically loaded from conftest.py

from momentum_client.manager import MomentumClientManager

def test_hent_virksomheder_with_filters(momentum_manager: MomentumClientManager):
    """Test hent_virksomheder with custom filters and search term."""
    filters = [
        {
            "customFilter": "active",
            "fieldName": "tags/id",
            "values": [
                None,
                None,
                None,
                None,
                "6f148a35-5a47-40d1-9b7e-a3a42e93eeff"
            ]
        },
    ]
    response = momentum_manager.virksomheder.hent_virksomheder(filters=filters)
    assert response is not None
    assert len(response["data"]) >= 2

def test_hent_virksomheder_med_cvr(momentum_manager: MomentumClientManager):
    """Test hent_virksomheder_med_cvr with specific CVR number."""
    cvr = "29190909"
    response = momentum_manager.virksomheder.hent_virksomheder_med_cvr(cvr)
    assert response is not None

def test_hent_virksomhed_med_markering_passiv_virksomhedsbank(momentum_manager: MomentumClientManager, test_virksomhedsid):
    """specifik markeringsid: """

    filters = [
    {
        "customFilter": "active",
        "fieldName": "tags/id",
        "values": [
            None,
            None,
            None,
            None,
            test_virksomhedsid
        ]
    },
    ]
    response = momentum_manager.virksomheder.hent_virksomheder(filters=filters)
    assert response is not None

def test_find_borgere_i_tilbud_på_virksomhed(momentum_manager: MomentumClientManager, test_virksomhedsid):
    """Test find_borgere_i_tilbud_på_virksomhed with empty filters."""
    # You will handle virksomhed yourself
    virksomhed = {
        "productionUnitId": test_virksomhedsid
    }
    
    filters = []
    
    response = momentum_manager.virksomheder.find_borgere_i_tilbud_på_virksomhed(
        virksomhed=virksomhed,
        filters=filters
    )
    assert response is not None
    assert len(response["data"]) > 20

def test_find_jobordre_på_virksomhed(momentum_manager: MomentumClientManager, test_virksomhedsid):
    """Test find_jobordre_på_virksomhed with empty filters."""
    # Use the same productionUnitId as the borgere test
    virksomhed = {
        "productionUnitId": test_virksomhedsid
    }
    
    filters = []
    
    response = momentum_manager.virksomheder.find_jobordre_på_virksomhed(
        virksomhed=virksomhed,
        filters=filters
    )
    assert response is not None
    assert len(response["data"]) > 100
    



