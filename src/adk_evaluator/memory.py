from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class MemorySnapshot:
    state: Dict[str, Any]


class AgentMemory:
    def __init__(self, initial_state: Optional[Dict[str, Any]] = None) -> None:
        self._store: Dict[str, Any] = deepcopy(initial_state or {})

    def read(self, key: str, default: Any = None) -> Any:
        return deepcopy(self._store.get(key, default))

    def write(self, key: str, value: Any) -> None:
        self._store[key] = deepcopy(value)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()

    def has(self, key: str) -> bool:
        return key in self._store

    def merge(self, updates: Dict[str, Any]) -> None:
        for key, value in updates.items():
            self.write(key, value)

    def snapshot(self) -> MemorySnapshot:
        return MemorySnapshot(state=deepcopy(self._store))
