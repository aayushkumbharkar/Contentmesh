"""Safety assertions against real FalkorDB; no mocked graph responses."""
from uuid import uuid4

import pytest

from app.graph import GraphStore
from app.memory import create_memory, update_memory


@pytest.fixture
def graphs():
    store = GraphStore()
    first, second = ('safety-' + uuid4().hex[:16] for _ in range(2))
    assert store.health(), 'Real FalkorDB is required for these tests'
    store.seed(first)
    store.seed(second)
    yield store, first, second
    for workspace in (first, second):
        store.db.select_graph('contextmesh_' + workspace).delete()


def test_unsafe_identifiers_and_literal_ids_preserve_graph(graphs):
    store, workspace, other = graphs
    before = store.graph(workspace)
    for invalid in ('../acmeshop', 'UPPER', '', 'a'*65, 'name; MATCH (n) DELETE n'):
        with pytest.raises(ValueError):
            store.graph(invalid)
    with pytest.raises(ValueError):
        store.put_node(workspace, 'Entity) DELETE n //', {'text': 'unsafe label'})
    with pytest.raises(ValueError):
        store.put_node(workspace, 'Entity', {'text = 1 DELETE n': 'unsafe property'})
    with pytest.raises(ValueError):
        store.link(workspace, 'checkout-api', 'maya-chen', 'OWNED_BY] DELETE n')
    payload = "x'} MATCH (n) DETACH DELETE n //"
    literal = store.put_node(workspace, 'Memory', {'id': payload, 'text': payload})
    assert store.get_node(workspace, payload)['text'] == payload
    assert store.get_node(other, payload) is None
    assert set(n['id'] for n in before['nodes']) <= set(n['id'] for n in store.graph(workspace)['nodes'])
    assert len(store.graph(workspace)['edges']) == len(before['edges'])
    assert literal['id'] == payload


def test_memory_revision_paths_and_neighborhood_are_workspace_local(graphs):
    store, workspace, other = graphs
    session = store.put_node(workspace, 'Session', {'label': 'Private session'})
    note = create_memory(store, workspace, session['id'], 'Private checkout finding marker-redwood')
    store.link(workspace, note['id'], 'checkout-api', 'MENTIONS')
    updated = update_memory(store, workspace, note['id'], 'Corrected private finding marker-redwood')
    assert updated['revision'] == 2
    revisions = [n for n in store.nodes(workspace, 'Evidence') if n.get('memory_id') == note['id']]
    assert len(revisions) == 1
    assert revisions[0]['text'] == note['text']
    assert revisions[0]['source'] == 'memory_revision'
    assert revisions[0]['trusted'] is False
    assert updated['trusted'] is False
    assert store.paths(workspace, revisions[0]['id'], note['id'])
    assert store.neighborhood(other, note['id']) == {'nodes': [], 'edges': []}
    assert store.paths(other, note['id'], 'checkout-api') == []
    assert store.paths(other, revisions[0]['id'], note['id']) == []
    assert store.retrieve(other, 'marker-redwood') == {'nodes': [], 'edges': [], 'paths': []}
    with pytest.raises(LookupError):
        update_memory(store, other, note['id'], 'cross-tenant overwrite')
    assert store.get_node(workspace, note['id'])['text'] == updated['text']


def test_bounded_retrieval_paths_are_supported_by_returned_edges(graphs):
    store, workspace, _ = graphs
    for index in range(48):
        node = store.put_node(workspace, 'Evidence', {'label': f'Checkout bounded fact {index}', 'text': 'Checkout observation'})
        store.link(workspace, node['id'], 'checkout-api', 'AFFECTS')
    for limit in (3, 20, 10000):
        result = store.retrieve(workspace, 'Checkout', limit=limit)
        assert len(result['nodes']) <= min(limit, 40)
        assert len(result['paths']) <= 24
        ids = {n['id'] for n in result['nodes']}
        assert all(e['source'] in ids and e['target'] in ids for e in result['edges'])
        for path in result['paths']:
            assert set(path['nodes']) <= ids
            assert 1 <= len(path['edges']) <= 3
            assert len(path['nodes']) == len(path['edges']) + 1
            for index, relationship in enumerate(path['edges']):
                assert any(e['type'] == relationship and {e['source'], e['target']} == set(path['nodes'][index:index+2]) for e in result['edges'])


def test_unrelated_query_and_disconnected_fact_do_not_fabricate_sources(graphs):
    store, workspace, _ = graphs
    assert store.retrieve(workspace, 'quasarzebraquantum') == {'nodes': [], 'edges': [], 'paths': []}
    isolated = store.put_node(workspace, 'Evidence', {'label': 'quasarzebraquantum', 'text': 'An unrelated isolated observation'})
    result = store.retrieve(workspace, 'quasarzebraquantum')
    assert [n['id'] for n in result['nodes']] == [isolated['id']]
    assert result['paths'] == []
    assert result['edges'] == []
    assert store.paths(workspace, isolated['id'], 'checkout-api') == []
