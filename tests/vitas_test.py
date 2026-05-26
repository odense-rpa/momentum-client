# Fixtures are automatically loaded from conftest.py

import datetime
from momentum_client.manager import MomentumClientManager

def test_hent_vitas_intet_søgeterm(momentum_manager: MomentumClientManager):
    response = momentum_manager.vitas.hent_vitas()
    assert response is not None

def test_hent_vitas_søgeterm(momentum_manager: MomentumClientManager):
    response = momentum_manager.vitas.hent_vitas("personlig")
    assert response is not None

def test_hent_vitas_med_filtre(momentum_manager: MomentumClientManager):
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%dT22:00:00.000Z")
    filters = [
        {
            "fieldName": "end",
            "values": [tomorrow, None, "false"]
        }
    ]
    response = momentum_manager.vitas.hent_vitas(filters=filters, søgeterm="personlig")
    assert response is not None

def test_hent_vita(momentum_manager: MomentumClientManager):
    id = "818dad74-951a-4396-a2f6-ba3976714bfd"
    response = momentum_manager.vitas.hent_vita(id)
    assert response is not None

def test_hent_vita_med_anden_type(momentum_manager: MomentumClientManager):
    id = "074da035-29a8-4636-ba22-2304e48859ca"
    type = "joballocation"
    response = momentum_manager.vitas.hent_vita(id, type=type)
    assert response is not None