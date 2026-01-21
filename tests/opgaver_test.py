import pytest
from momentum_client.manager import MomentumClientManager

def test_opret_opgave(momentum_manager: MomentumClientManager, test_cpr):
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

def test_hent_opgaver(momentum_manager: MomentumClientManager, test_cpr):
    borger = momentum_manager.borgere.hent_borger(test_cpr)

    opgaver = momentum_manager.opgaver.hent_opgaver(borger=borger)

    assert isinstance(opgaver, list)
