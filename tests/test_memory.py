from adk_evaluator.memory import AgentMemory


def test_agent_memory_write_read_delete():
    memory = AgentMemory()
    assert not memory.has("mission")

    memory.write("mission", {"step": 1, "target": "A"})
    assert memory.has("mission")
    assert memory.read("mission") == {"step": 1, "target": "A"}

    memory.delete("mission")
    assert not memory.has("mission")
    assert memory.read("mission", default={}) == {}


def test_agent_memory_merge_and_snapshot_isolation():
    memory = AgentMemory({"position": {"x": 0, "y": 0}})
    memory.merge({"position": {"x": 1, "y": 1}, "status": "active"})

    snapshot = memory.snapshot()
    assert snapshot.state == {"position": {"x": 1, "y": 1}, "status": "active"}

    snapshot.state["position"]["x"] = 99
    assert memory.read("position") == {"x": 1, "y": 1}


def test_agent_memory_clear_resets_state():
    memory = AgentMemory({"mode": "search", "progress": 50})
    memory.clear()
    assert memory.snapshot().state == {}
    assert memory.read("mode") is None
