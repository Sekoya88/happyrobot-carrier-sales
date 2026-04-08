import json
from typing import Optional
from domain.entities import Load


class LoadRepository:
    def __init__(self, loads_file: str = "data/loads.json"):
        with open(loads_file) as f:
            raw = json.load(f)
        self._loads = [Load(**item) for item in raw]

    def search(
        self,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        equipment_type: Optional[str] = None,
    ) -> list[Load]:
        results = self._loads
        if origin:
            results = [l for l in results if origin.lower() in l.origin.lower()]
        if destination:
            results = [l for l in results if destination.lower() in l.destination.lower()]
        if equipment_type:
            results = [l for l in results if l.equipment_type.lower() == equipment_type.lower()]
        return results

    def get_by_id(self, load_id: str) -> Optional[Load]:
        return next((l for l in self._loads if l.load_id == load_id), None)
