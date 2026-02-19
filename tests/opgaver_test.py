import pytest
from momentum_client.manager import MomentumClientManager

def test_opret_opgave_på_borger(momentum_manager: MomentumClientManager, test_cpr):
    borger = momentum_manager.borgere.hent_borger(test_cpr)
    sagsbehandler = momentum_manager.borgere.hent_sagsbehandler("jakkw")
    medarbejdere = [sagsbehandler] if sagsbehandler else []

    from datetime import datetime, timedelta
    forfaldsdato = datetime.now() + timedelta(days=7)
    titel = "Test Opgave"
    beskrivelse = "Dette er en test opgave oprettet via unit test."

    opgave = momentum_manager.opgaver.opret_opgave(
        borger=borger,
        medarbejdere=medarbejdere,
        forfaldsdato=forfaldsdato,
        titel=titel,
        beskrivelse=beskrivelse
    )

    assert opgave is not None
    assert opgave.get("title") == titel
    assert opgave.get("description") == beskrivelse

def test_opret_opgave_på_virksomhed(momentum_manager: MomentumClientManager):
    virkomshed = momentum_manager.virksomheder.hent_virksomhed_med_cvr_og_pnummer("35954716", "1003225055")
    sagsbehandler = momentum_manager.borgere.hent_sagsbehandler("andja")
    medarbejdere = [sagsbehandler]

    from datetime import datetime, timedelta
    forfaldsdato = datetime.now() + timedelta(days=7)
    titel = "Test Opgave"
    beskrivelse = "Dette er en test opgave oprettet via unit test."

    opgave = momentum_manager.opgaver.opret_opgave(
        borger=virkomshed,
        medarbejdere=medarbejdere,
        forfaldsdato=forfaldsdato,
        titel=titel,
        beskrivelse=beskrivelse,
        borger_opgave=False
    )

    assert opgave is not None
    assert opgave.get("title") == titel
    assert opgave.get("description") == beskrivelse

def test_hent_opgaver(momentum_manager: MomentumClientManager, test_cpr):
    borger = momentum_manager.borgere.hent_borger(test_cpr)

    opgaver = momentum_manager.opgaver.hent_opgaver(borger=borger)

    assert isinstance(opgaver, list)

def test_opdater_opgavestatus(momentum_manager: MomentumClientManager):
    status = momentum_manager.opgaver.Status.gennemført
    opgaveid = ""

    response = momentum_manager.opgaver.opdater_opgave_status(opgaveid, status)

    assert response is not None

def test_hent_opgaver_på_virksomhed(momentum_manager: MomentumClientManager):
    virksomhedsid = "00a69184-d845-4a20-9027-1566b9f6d9cf"

    response = momentum_manager.opgaver.hent_opgaver_på_virksomhed(virksomhedsid)

    assert response is not None
    assert len(response) > 2