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
                "b0c52d99-f739-49d8-8532-417f224fa757"
            ]
        },
    ]
    response = momentum_manager.virksomheder.hent_virksomheder(filters=filters)
    assert response is not None


