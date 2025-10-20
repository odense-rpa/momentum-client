# Fixtures are automatically loaded from conftest.py

import datetime
from momentum_client.manager import MomentumClientManager


def test_hent_borger(momentum_manager: MomentumClientManager, test_cpr):
    # Test with a valid TEST CPR number
    response = momentum_manager.borgere.hent_borger(test_cpr)
    assert response is not None    

def test_hent_borgere(momentum_manager: MomentumClientManager):
    filters = [
        {
            "customFilter": "",
            "fieldName": "targetGroupCode",
            "values": [
                "6.6",
            ]
        },
    ]
    response = momentum_manager.borgere.hent_borgere(filters)
    assert response is not None

# Test hent_markering med default markeringsnavn
def test_hent_markering(momentum_manager: MomentumClientManager):
    response = momentum_manager.borgere.hent_markering()
    assert response is not None

# Test hent_markering med et specifikt markeringsnavn
def test_hent_markering_specific(momentum_manager: MomentumClientManager):
    response = momentum_manager.borgere.hent_markering("1. fællessamtale i jobcentret gennemført")
    assert response is not None
    assert response.get("title") == "1. fællessamtale i jobcentret gennemført"

def test_opret_markering(momentum_manager: MomentumClientManager, test_cpr):
    # Test opret_markering med en gyldig markering
    markeringsnavn = "Teknisk forlængelse - sygedagpenge"
    # IKKE COMMIT CPR-nummer i test
    borger = momentum_manager.borgere.hent_borger(test_cpr)
    start_dato = datetime.date.today()

    response = momentum_manager.borgere.opret_markering(markeringsnavn, borger, start_dato)
    assert response is not None

    slettet_markering = momentum_manager.borgere.slet_markering(response["id"])
    assert slettet_markering is True

def test_afslut_markering(momentum_manager: MomentumClientManager, test_cpr):
    # IKKE COMMIT CPR-nummer i test
    borger = momentum_manager.borgere.hent_borger(test_cpr)
    borgers_markeringer = momentum_manager.borgere.hent_markeringer(borger)
    slut_dato = datetime.datetime.today()

    test_markering = next((markering for markering in borgers_markeringer if markering['tag']['title'] == "Teknisk forlængelse - sygedagpenge" and markering['end'] is None), None)
    assert test_markering is not None

    afsluttet_markering = momentum_manager.borgere.afslut_markering(test_markering, slut_dato)
    assert afsluttet_markering is not None

def test_opret_notifikation(momentum_manager: MomentumClientManager, test_cpr):
    # IKKE COMMIT CPR-nummer i test
    borger = momentum_manager.borgere.hent_borger(test_cpr)  # TODO: Replace with actual test CPR
    start_dato = datetime.date.today()
    slut_dato = start_dato + datetime.timedelta(days=7)

    response = momentum_manager.borgere.opret_notifikation(
        borger=borger,
        titel="Test Notifikation",
        start_dato=start_dato,
        slut_dato=slut_dato,
        vigtighed_af_notifikation="info",
        beskrivelse="2025-08-18 2",
        synlig_i_header=True
    )
    assert response is not None

def test_opdater_borgers_ansvarlige_og_kontaktpersoner(momentum_manager: MomentumClientManager, test_cpr):
    borger = momentum_manager.borgere.hent_borger(test_cpr)
    response = momentum_manager.borgere.opdater_borgers_ansvarlige_og_kontaktpersoner(
        borger=borger,
        medarbejderid="476ebc9c-969d-424c-92f0-d582bf6176bb"
    )
    assert response is not None

def test_søg_mange_resultater(momentum_manager: MomentumClientManager):
    response = momentum_manager.momentum_client.søg(søgeterm="Odense", kategori="Company")
    assert response is not None

def test_søg_flere_resultater_end_batch_størrelse(momentum_manager: MomentumClientManager):
    response = momentum_manager.momentum_client.søg(søgeterm="Odense", kategori="Company", ønsket_antal=500)
    assert response is not None

def test_søg_et_resultat(momentum_manager: MomentumClientManager, test_cpr):
    response = momentum_manager.momentum_client.søg(søgeterm=test_cpr, kategori="Citizen")
    assert response is not None

def test_søg_ingen_resultater(momentum_manager: MomentumClientManager):
    response = momentum_manager.momentum_client.søg(søgeterm="DetteCprFindesIkke123", kategori="Citizen")
    assert response is not None