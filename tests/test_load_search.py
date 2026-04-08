import pytest
from infrastructure.load_repository import LoadRepository


def test_search_by_origin_destination():
    repo = LoadRepository(loads_file="data/loads.json")
    results = repo.search(origin="Chicago", destination="Dallas")
    assert len(results) >= 1
    assert "chicago" in results[0].origin.lower()


def test_search_by_equipment_type():
    repo = LoadRepository(loads_file="data/loads.json")
    results = repo.search(origin="Chicago", destination="Dallas", equipment_type="Dry Van")
    assert all(r.equipment_type == "Dry Van" for r in results)
