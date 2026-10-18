"""Workflow checks use real persistence; injected failures never replace the graph."""
import json
from uuid import uuid4

import pytest

from app.graph import GraphStore, GraphUnavailable
from app.orchestration import run_workflow


@pytest.fixture
def graph_workspace():
    store = GraphStore()
    workspace = "workflow-" + uuid4().hex[:12]
    assert store.health(), "Real FalkorDB is required"
    session = store.put_node(workspace, "Session", {"label": "Workflow verification"})
    yield store, workspace, session["id"]
    store.db.select_graph("contextmesh_" + workspace).delete()


def test_conflicting_owner_and_current_config_are_flagged(graph_workspace):
    store, workspace, session = graph_workspace
    store.seed(workspace)
    result = run_workflow(store, workspace, session,
                          "John Smith owns Checkout API. Redis TTL is now 30 seconds. Investigate release 2.4.")
    assert any("John Smith" in conflict for conflict in result["conflicts"])
    assert any("60 seconds" in conflict for conflict in result["conflicts"])
    assert "not proven causes" in result["answer"]
    verifier = store.get_node(workspace, result["steps"][-1]["id"])
    assert json.loads(verifier["output"])["conflicts"] == result["conflicts"]


def test_missing_evidence_never_fabricates_paths_or_answers(graph_workspace):
    store, workspace, session = graph_workspace
    result = run_workflow(store, workspace, session, "Explain the unknown meteor anomaly")
    assert result["evidence"] == []
    assert result["paths"] == []
    assert "insufficient evidence" in result["answer"]
    assert "Maya" not in result["answer"]
    tasks = store.nodes(workspace, "Task")
    assert any("missing" in task["label"] for task in tasks)
    assert sum(task["status"] == "blocked" for task in tasks) == 2
    assert len(result["gaps"]) == 3


def test_graph_failure_persists_failed_run_without_secret(graph_workspace, monkeypatch):
    store, workspace, session = graph_workspace

    def unavailable(*args, **kwargs):
        raise GraphUnavailable("private-database-password")

    monkeypatch.setattr(store, "retrieve", unavailable)
    with pytest.raises(GraphUnavailable):
        run_workflow(store, workspace, session, "Checkout API investigation")
    runs = GraphStore().nodes(workspace, "Run")
    assert len(runs) == 1 and runs[0]["status"] == "failed"
    assert "private-database-password" not in runs[0]["error"]
    assert "completed_at" in runs[0]


def test_initial_session_link_failure_marks_created_run_failed(graph_workspace, monkeypatch):
    store, workspace, session = graph_workspace
    original_link = store.link
    failures = []

    def fail_initial_link(workspace_id, source, target, relationship):
        if relationship == "HAS_RUN" and not failures:
            failures.append(target)
            raise GraphUnavailable("Transient initial relationship failure")
        return original_link(workspace_id, source, target, relationship)

    monkeypatch.setattr(store, "link", fail_initial_link)
    with pytest.raises(GraphUnavailable):
        run_workflow(store, workspace, session, "Investigate Checkout API")
    assert len(failures) == 1
    run = GraphStore().get_node(workspace, failures[0])
    assert run["status"] == "failed"
    assert run["session_id"] == session
    assert run["completed_at"]
    assert store.nodes(workspace, "Memory") == []


def test_missing_persisted_handoff_prevents_downstream_work(graph_workspace, monkeypatch):
    store, workspace, session = graph_workspace
    store.seed(workspace)
    get_node = store.get_node
    reads = []

    def interrupt_handoff(workspace_id, node_id):
        node = get_node(workspace_id, node_id)
        if node and node["kind"] == "AgentRun":
            reads.append(node_id)
            return None
        return node

    monkeypatch.setattr(store, "get_node", interrupt_handoff)
    with pytest.raises(RuntimeError, match="handoff"):
        run_workflow(store, workspace, session, "Investigate Checkout API")
    assert reads
    fresh = GraphStore()
    assert fresh.nodes(workspace, "Run")[0]["status"] == "failed"
    assert len(fresh.nodes(workspace, "AgentRun")) == 1
    assert fresh.nodes(workspace, "Task") == []


def test_provider_context_is_bounded_and_failure_preserves_evidence(graph_workspace):
    store, workspace, session = graph_workspace
    store.seed(workspace)
    contexts = []

    def failing_provider(context):
        contexts.append(context)
        raise TimeoutError("Provider timeout")

    result = run_workflow(store, workspace, session, "Checkout API " * 800, failing_provider)
    assert len(contexts) == 1
    assert len(contexts[0]["question"]) <= 2000
    assert len(contexts[0]["facts"]) <= 12
    assert all(len(fact["text"]) <= 500 for fact in contexts[0]["facts"])
    assert result["status"] == "completed"
    assert result["usage"]["fallback_reason"] == "provider_unavailable"
    assert result["evidence"] and result["paths"]
    assert "Maya Chen" in result["answer"]
    assert json.loads(GraphStore().get_node(workspace, result["id"])["result"])["usage"] == result["usage"]


def test_handoffs_and_task_dependencies_reference_persisted_records(graph_workspace):
    store, workspace, session = graph_workspace
    store.seed(workspace)
    result = run_workflow(store, workspace, session, "Investigate Checkout API release 2.4")
    graph = GraphStore().graph(workspace)
    for previous, current in zip(result["steps"], result["steps"][1:]):
        assert previous["id"] in current["input_ids"]
        assert any(edge["source"] == previous["id"] and edge["target"] == current["id"]
                   and edge["type"] == "HANDOFF_TO" for edge in graph["edges"])
        output = json.loads(store.get_node(workspace, previous["id"])["output"])
        assert output["evidence_ids"]
    assert sum(edge["type"] == "DEPENDS_ON" for edge in graph["edges"]) == 2
    tasks = store.nodes(workspace, "Task")
    assert any(any(edge["type"] == "OWNED_BY" for edge in json.loads(task["basis"])) for task in tasks)


def test_prior_decisions_are_not_recycled_as_evidence_and_mentions_are_explicit(graph_workspace):
    store, workspace, session = graph_workspace
    store.seed(workspace)
    note = "Checkout API unique canary cart-729 failed after release 2.4"
    first = run_workflow(store, workspace, session, note)
    next_session = store.put_node(workspace, "Session", {"label": "Fresh session"})
    second = run_workflow(GraphStore(), workspace, next_session["id"], "Explain Checkout API failure and earlier lessons")
    assert all(node["kind"] != "Decision" for node in second["evidence"])
    assert any("cart-729" in node.get("text", "") for node in second["evidence"])
    assert "Unverified user note" in second["answer"]
    memory = next(node for node in store.nodes(workspace, "Memory") if node["text"] == note)
    mentions = [edge["target"] for edge in store.graph(workspace)["edges"]
                if edge["source"] == memory["id"] and edge["type"] == "MENTIONS"]
    assert "checkout-api" in mentions
    assert "maya-chen" not in mentions
    assert "incident-current" not in mentions
