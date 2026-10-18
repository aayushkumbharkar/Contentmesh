"""Durable memory with immutable revision provenance in the workspace graph."""
from datetime import datetime, timezone


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def create_memory(store, workspace_id, session_id, text, run_id=None):
    session = store.get_node(workspace_id, session_id)
    if not session or session.get("kind") != "Session":
        raise LookupError("Session not found in this workspace")
    memory = store.put_node(workspace_id, "Memory", {
        "label": text[:90], "text": text, "session_id": session_id,
        "created_at": timestamp(), "source": "user_note", "trusted": False,
        "run_id": run_id or "", "revision": 1,
    })
    store.link(workspace_id, session_id, memory["id"], "HAS_MEMORY")
    if run_id:
        store.link(workspace_id, run_id, memory["id"], "GENERATED")
    return memory


def update_memory(store, workspace_id, memory_id, text):
    """Keep the prior contents as an Evidence node before updating a memory."""
    memory = store.get_node(workspace_id, memory_id)
    if not memory or memory.get("kind") != "Memory":
        raise LookupError("Memory not found in this workspace")
    prior = store.put_node(workspace_id, "Evidence", {
        "label": "Previous memory revision", "text": memory.get("text", ""),
        "source": "memory_revision", "trusted": False, "memory_id": memory_id,
        "revision": memory.get("revision", 1), "created_at": timestamp(),
    })
    store.link(workspace_id, prior["id"], memory_id, "SUPPORTS")
    return store.put_node(workspace_id, "Memory", {
        **memory, "text": text, "label": text[:90], "updated_at": timestamp(),
        "revision": int(memory.get("revision", 1)) + 1,
    })
