from momentum_client.manager import MomentumClientManager


def test_hent_alle_taksonomier(momentum_manager: MomentumClientManager):
    response = momentum_manager.taksonomier.hent_alle_taksonomier()

    # Find where name is "Porteføljeansvarlig" in nested items
    portefoljeansvarlig = []
    for taxonomy_group in response:
        for item in taxonomy_group.get("items", []):
            if item.get("name") == "Porteføljeansvarlig":
                portefoljeansvarlig.append({
                    "taxonomy_group": taxonomy_group["name"],
                    "taxonomy_code": taxonomy_group["code"],
                    "item": item
                })
    assert response is not None
    assert len(response) > 100
    assert len(portefoljeansvarlig) == 1
    
def test_hent_taxanomi_gruppe(momentum_manager: MomentumClientManager):
    test_tax_kode = "CAUSE_TYPE"
    response = momentum_manager.taksonomier.find_taksonomi_gruppe(test_tax_kode)
    assert response is not None
    assert response["name"] == "Cause Types" and response["code"] == test_tax_kode