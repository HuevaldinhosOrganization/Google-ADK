from adk_evaluator.memory import AgentMemory


def test_agent_memory_write_read_delete():
    """Test basic AgentMemory write, read, and delete operations.
    
    Verifies:
    - write() stores values and has() confirms existence
    - read() retrieves stored values with deep copy isolation
    - delete() removes values and read() returns default when missing
    """
    memory = AgentMemory()
    assert not memory.has("mission")

    memory.write("mission", {"step": 1, "target": "A"})
    assert memory.has("mission")
    assert memory.read("mission") == {"step": 1, "target": "A"}

    memory.delete("mission")
    assert not memory.has("mission")
    assert memory.read("mission", default={}) == {}


def test_agent_memory_merge_and_snapshot_isolation():
    """Test AgentMemory merge and snapshot with isolation guarantees.
    
    Verifies:
    - merge() combines multiple key-value pairs into memory
    - snapshot() captures current state as MemorySnapshot
    - Deep copy isolation: modifying snapshot doesn't affect memory
    """
    memory = AgentMemory({"position": {"x": 0, "y": 0}})
    memory.merge({"position": {"x": 1, "y": 1}, "status": "active"})

    snapshot = memory.snapshot()
    assert snapshot.state == {"position": {"x": 1, "y": 1}, "status": "active"}

    snapshot.state["position"]["x"] = 99
    assert memory.read("position") == {"x": 1, "y": 1}


def test_agent_memory_clear_resets_state():
    """Test that AgentMemory.clear() removes all stored state.
    
    Verifies:
    - clear() removes all key-value pairs
    - snapshot() after clear returns empty state
    - read() returns None for non-existent keys after clear
    """
    memory = AgentMemory({"mode": "search", "progress": 50})
    memory.clear()
    assert memory.snapshot().state == {}
    assert memory.read("mode") is None
