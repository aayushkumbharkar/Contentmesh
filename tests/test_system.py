"""Integration checks require real FalkorDB; unavailable database fails, never mocks."""
import json
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from app.main import app, store
from app.graph import GraphStore, GraphUnavailable, validate_workspace
from app.provider import synthesize

@pytest.fixture
def workspace():
    identifier = 'test-' + uuid4().hex[:12]
    store.seed(identifier)
    yield identifier
    # Only delete this fixture's exact, generated graph.
    store.db.select_graph('contextmesh_' + identifier).delete()

@pytest.fixture
def client():
    return TestClient(app)

def test_real_graph_roundtrip_and_paths(workspace):
    assert store.health()
    initial = store.graph(workspace)
    store.seed(workspace)
    assert len(initial['nodes']) == len(store.graph(workspace)['nodes'])
    paths = store.paths(workspace, 'redis-change', 'maya-chen', 3)
    assert any(p['nodes'] == ['redis-change', 'checkout-api', 'maya-chen'] for p in paths)
    for path in paths:
        for i, edge in enumerate(path['edges']):
            assert any(e['type'] == edge and {e['source'], e['target']} == set(path['nodes'][i:i+2]) for e in initial['edges'])
    assert len(store.neighborhood(workspace, 'checkout-api')['nodes']) > 3
    fresh = GraphStore()
    assert fresh.get_node(workspace, 'redis-change')['text'] == store.get_node(workspace, 'redis-change')['text']

def test_two_sessions_and_saved_handoffs(client, workspace):
    base = '/api/workspaces/' + workspace
    first = client.post(base + '/sessions', json={'title':'Incident note'}).json()
    note = 'Checkout API failed after release 2.4. Observed unique marker cart-omega-729 in session expiry logs.'
    response = client.post(base + '/sessions/' + first['id'] + '/runs', json={'text':note})
    assert response.status_code == 200, response.text
    result1 = response.json()
    assert result1['status'] == 'completed'
    second = client.post(base + '/sessions', json={'title':'Fresh investigation'}).json()
    result = client.post(base + '/sessions/' + second['id'] + '/runs', json={'text':'Which previous change could explain the Checkout API incident, who owns it, and what was learned earlier?'}).json()
    assert result['status'] == 'completed'
    assert len(result['steps']) == 4
    assert 'Maya Chen' in result['answer']
    assert '3600' in result['answer']
    assert any('cart-omega-729' in n.get('text','') for n in result['evidence'])
    assert result['paths']
    assert len(client.get(base + '/runs').json()['runs']) == 2
    graph = store.graph(workspace)
    assert sum(e['type'] == 'HANDOFF_TO' for e in graph['edges']) == 6
    for step in result['steps']:
        saved = store.get_node(workspace, step['id'])
        assert json.loads(saved['output'])
    memory = next(n for n in store.nodes(workspace, 'Memory') if n.get('text') == note)
    revised = client.patch(base + '/memories/' + memory['id'], json={'text':note + ' Correction: only sandbox purchases affected.'})
    assert revised.status_code == 200
    assert any(n.get('text') == note for n in store.nodes(workspace, 'Evidence'))

def test_workspace_isolation_and_injection(client, workspace):
    base = '/api/workspaces/' + workspace
    session = client.post(base + '/sessions', json={'title':'Private'}).json()
    other = 'empty-' + uuid4().hex[:12]
    try:
        assert store.get_node(other, session['id']) is None
        assert store.paths(other, 'redis-change', 'maya-chen') == []
        assert client.post('/api/workspaces/' + other + '/sessions/' + session['id'] + '/runs', json={'text':'private'}).status_code == 404
        attack = "Robert'); MATCH (n) DETACH DELETE n //"
        node = store.put_node(workspace, 'Memory', {'text':attack, 'label':'untrusted'})
        assert store.get_node(workspace, node['id'])['text'] == attack
        assert store.get_node(workspace, 'checkout-api')
        with pytest.raises(ValueError):
            store.link(workspace, node['id'], 'checkout-api', 'RELATES_TO] DELETE n')
        with pytest.raises(ValueError):
            validate_workspace('../acmeshop')
    finally:
        store.db.select_graph('contextmesh_' + other).delete()

def test_api_validation_and_database_error(client, monkeypatch):
    assert client.post('/api/workspaces/INVALID/sessions', json={}).status_code == 422
    assert client.post('/api/workspaces/acmeshop/sessions/nope/runs', json={'text':'x'*6001}).status_code == 422
    def fail(*args, **kwargs):
        raise GraphUnavailable('secret internal connection string')
    monkeypatch.setattr(store, 'graph', fail)
    result = client.get('/api/workspaces/acmeshop/graph')
    assert result.status_code == 503
    assert 'secret' not in result.text

def test_provider_fallback_and_budget(monkeypatch):
    monkeypatch.setenv('LLM_PROVIDER', 'demo')
    assert synthesize({})['usage']['calls'] == 0
    monkeypatch.setenv('LLM_PROVIDER', 'groq')
    monkeypatch.delenv('GROQ_API_KEY', raising=False)
    result = synthesize({})
    assert result['usage']['calls'] == 0
    assert result['warning']
