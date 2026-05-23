from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class MemorySnapshot:
    state: Dict[str, Any]


class AgentMemory:
    """Manages agent state with deep copy isolation."""
    def __init__(self, initial_state: Optional[Dict[str, Any]] = None) -> None:
        """Initialize AgentMemory with optional initial state.
        
        Args:
            initial_state: Initial memory state dictionary. Defaults to empty dict.
        """
        self._store: Dict[str, Any] = deepcopy(initial_state or {})

    def read(self, key: str, default: Any = None) -> Any:
        """Read a value from memory with deep copy protection.
        
        Args:
            key: Memory key to read.
            default: Default value if key doesn't exist.
        
        Returns:
            Deep copy of the stored value or default.
        """
        return deepcopy(self._store.get(key, default))

    def write(self, key: str, value: Any) -> None:
        """Write a value to memory with deep copy isolation.
        
        Args:
            key: Memory key to store value under.
            value: Value to store (will be deep copied).
        """
        self._store[key] = deepcopy(value)

    def delete(self, key: str) -> None:
        """Delete a key from memory.
        
        Args:
            key: Memory key to delete.
        """
        self._store.pop(key, None)

    def clear(self) -> None:
        """Clear all memory state."""
        self._store.clear()

    def has(self, key: str) -> bool:
        """Check if a key exists in memory.
        
        Args:
            key: Memory key to check.
        
        Returns:
            True if key exists, False otherwise.
        """
        return key in self._store

    def merge(self, updates: Dict[str, Any]) -> None:
        """Merge multiple key-value pairs into memory.
        
        Args:
            updates: Dictionary of key-value pairs to merge.
        """
        for key, value in updates.items():
            self.write(key, value)

    def snapshot(self) -> MemorySnapshot:
        """Create a snapshot of the current memory state.
        
        Returns:
            MemorySnapshot with a deep copy of current state.
        """
        return MemorySnapshot(state=deepcopy(self._store))
