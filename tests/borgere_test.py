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

def test_hent_sagsbehandler(momentum_manager: MomentumClientManager):
    response = momentum_manager.borgere.hent_sagsbehandler("jakkw")
    assert response is not None

def test_hent_sagsbehandler_med_nul_resultat(momentum_manager: MomentumClientManager):
    response = momentum_manager.borgere.hent_sagsbehandler("jakfvdgfdgkw")
    assert response is None

def test_hent_ansvarlig_sagsbehandlere(momentum_manager: MomentumClientManager, test_cpr):
    borger = momentum_manager.borgere.hent_borger(test_cpr)
    ansvarlige_sagsbehandlere = momentum_manager.borgere.hent_ansvarlige_sagsbehandlere(borger)
    assert ansvarlige_sagsbehandlere is not None

def test_hent_aktive_sagsbehandlere(momentum_manager: MomentumClientManager, test_cpr):
    borger = momentum_manager.borgere.hent_borger(test_cpr)
    aktive_sagsbehandlere = momentum_manager.borgere.hent_aktive_sagsbehandlere(borger)
    assert aktive_sagsbehandlere is not None

def test_hent_alle_private_kontaktpersoner(momentum_manager: MomentumClientManager, test_cpr):
    borger = momentum_manager.borgere.hent_borger(test_cpr)
    private_kontaktpersoner = momentum_manager.borgere.hent_alle_private_kontaktpersoner(borger)
    assert private_kontaktpersoner is not None

def test_søg_specifik_privat_kontaktperson(momentum_manager: MomentumClientManager, test_cpr):
    borger = momentum_manager.borgere.hent_borger(test_cpr)
    specifik_kontaktperson = momentum_manager.borgere.søg_specifik_privat_kontaktperson(
        borger=borger, søgeterm="unik"
    )
    assert specifik_kontaktperson is not None

def test_hent_aktør(momentum_manager: MomentumClientManager):
    aktør = momentum_manager.borgere.hent_aktør("1d8b1069-4844-4f5d-90df-649676df1907")
    assert aktør is not None

def test_opret_privat_kontaktperson(momentum_manager: MomentumClientManager, test_cpr):
    borger = momentum_manager.borgere.hent_borger(test_cpr)
    kontaktperson = momentum_manager.borgere.opret_privat_kontaktperson(
        borger=borger,
        navn="Test Kontaktperson",
        email="test.kontaktperson@example.com",
        telefon="12345678"
    )
    assert kontaktperson is not None

def test_tilføj_privat_kontaktperson_til_borger(momentum_manager: MomentumClientManager, test_cpr):
    borger = momentum_manager.borgere.hent_borger(test_cpr)
    # Opret først en privat kontaktperson
    kontaktperson = momentum_manager.borgere.opret_privat_kontaktperson(
        borger=borger,
        navn="bbb",
        email="test.tilføj.kontaktperson@example.com",
        telefon="87654321"
    )
    assert kontaktperson is not None
    # Tilføj derefter kontaktpersonen til borgeren
    tilføjet_kontaktperson = momentum_manager.borgere.opdater_borgers_ansvarlige_og_kontaktpersoner(
        borger=borger,
        medarbejderid=kontaktperson["id"],
        medarbejderrolle="DUBU-sagsbehandler",
        privat_kontaktperson=True
    )
    assert tilføjet_kontaktperson is not None

def test_inaktiver_privat_kontaktperson(momentum_manager: MomentumClientManager, test_cpr):
    borger = momentum_manager.borgere.hent_borger(test_cpr)
    kontaktperson_navn = "bugge2"
    inaktiveret = momentum_manager.borgere.inaktiver_privat_kontaktperson(
        borger=borger,
        kontaktperson_navn=kontaktperson_navn
    )
    assert inaktiveret is True

def test_fjern_ansvarlig_eller_privat_kontaktperson(momentum_manager: MomentumClientManager, test_cpr):
    borger = momentum_manager.borgere.hent_borger(test_cpr)
    # sagsbehandler_navn = "bugge2 ugge2"
    email_der_skal_fjernes = "123@34325.dk"
    fjernet = momentum_manager.borgere.fjern_ansvarlig_eller_privat_kontaktperson(
        borger=borger,
        email=email_der_skal_fjernes
    )
    assert fjernet is True

def test_hent_uddannelser(momentum_manager: MomentumClientManager, test_cpr):
    borger = momentum_manager.borgere.hent_borger(test_cpr)
    uddannelser = momentum_manager.borgere.hent_uddannelser(borger)
    assert uddannelser is not None