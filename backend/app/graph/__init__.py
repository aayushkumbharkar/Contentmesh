"""Tenant-isolated, bounded FalkorDB persistence. No in-memory fallback."""
import os
import re
from datetime import datetime, timezone
from uuid import uuid4

from falkordb import FalkorDB

KINDS = frozenset('Workspace Session Memory Evidence Entity Task Decision Agent AgentRun Run'.split())
RELATIONSHIPS = frozenset('HAS_SESSION MENTIONS RELATES_TO SUPPORTS DEPENDS_ON GENERATED HANDOFF_TO HAS_MEMORY HAS_RUN OWNED_BY AFFECTS RESOLVED_BY NEXT'.split())


class GraphUnavailable(RuntimeError):
    pass


def validate_workspace(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', value):
        raise ValueError('Workspace ID must contain 1–64 lowercase letters, digits or hyphens')
    return value


class GraphStore:
    def __init__(self):
        # Client construction probes Redis. Defer it so unavailable databases
        # do not crash application startup or bypass the safe health response.
        self.db = None
        self.connection = dict(host=os.getenv('FALKORDB_HOST', 'localhost'),
                               port=int(os.getenv('FALKORDB_PORT', '6379')),
                               password=os.getenv('FALKORDB_PASSWORD') or None,
                               socket_connect_timeout=3, socket_timeout=10)

    def _query(self, workspace, query, params=None):
        name = 'contextmesh_' + validate_workspace(workspace)
        try:
            if self.db is None:
                self.db = FalkorDB(**self.connection)
            return self.db.select_graph(name).query(query, params=params or {}, timeout=5000).result_set
        except Exception as exc:
            raise GraphUnavailable('Graph database operation failed; check database availability and server logs') from exc

    def health(self):
        try:
            return self._query('health', 'RETURN 1')[0][0] == 1
        except GraphUnavailable:
            return False

    @staticmethod
    def _node(node):
        return dict(node.properties)

    def put_node(self, workspace_id, kind, properties):
        if kind not in KINDS:
            raise ValueError('Unsupported node kind')
        props = dict(properties)
        if any(not isinstance(k, str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', k) for k in props):
            raise ValueError('Invalid property name')
        if any(v is not None and not isinstance(v, (str, bool, int, float)) for v in props.values()):
            raise ValueError('Properties must be flat scalar values')
        props['id'] = str(props.get('id') or uuid4())
        if len(props['id']) > 128:
            raise ValueError('Node ID too long')
        props['kind'] = kind
        props['updated_at'] = datetime.now(timezone.utc).isoformat()
        existing = self.get_node(workspace_id, props['id'])
        if existing and existing['kind'] != kind:
            raise ValueError('Node kind cannot change')
        props.setdefault('label', existing.get('label', kind) if existing else kind)
        props.setdefault('created_at', existing.get('created_at') if existing else props['updated_at'])
        # Property names are validated, values always parameters; avoids client map-literal incompatibilities.
        assignments = ', '.join(f'n.{key} = $p{idx}' for idx, key in enumerate(props))
        params = {f'p{idx}': value for idx, value in enumerate(props.values())}
        params['id'] = props['id']
        rows = self._query(workspace_id, f'MERGE (n:{kind} {{id: $id}}) SET {assignments} RETURN n', params)
        return self._node(rows[0][0])

    def get_node(self, workspace_id, id):
        rows = self._query(workspace_id, 'MATCH (n {id: $id}) RETURN n LIMIT 1', {'id': id})
        return self._node(rows[0][0]) if rows else None

    def nodes(self, workspace_id, kind=None, limit=200):
        if kind is not None and kind not in KINDS:
            raise ValueError('Unsupported node kind')
        limit = max(1, min(int(limit), 500))
        label = ':' + kind if kind else ''
        return [self._node(r[0]) for r in self._query(workspace_id, f'MATCH (n{label}) RETURN n ORDER BY n.updated_at DESC, n.id LIMIT {limit}')]

    def link(self, workspace_id, source_id, target_id, relationship):
        if relationship not in RELATIONSHIPS:
            raise ValueError('Unsupported relationship')
        rows = self._query(workspace_id, f'MATCH (s {{id: $s}}), (t {{id: $t}}) MERGE (s)-[r:{relationship}]->(t) RETURN s.id, t.id, type(r)', {'s': source_id, 't': target_id})
        if not rows:
            raise ValueError('Relationship endpoints must exist in this workspace')
        return self._edge(*rows[0])

    @staticmethod
    def _edge(source, target, relationship):
        return {'id': f'{source}:{relationship}:{target}', 'source': source, 'target': target, 'type': relationship}

    def _subgraph(self, workspace, ids):
        if not ids:
            return {'nodes': [], 'edges': []}
        nodes = [self._node(r[0]) for r in self._query(workspace, 'MATCH (n) WHERE n.id IN $ids RETURN n', {'ids': ids})]
        edges = [self._edge(*r) for r in self._query(workspace, 'MATCH (s)-[r]->(t) WHERE s.id IN $ids AND t.id IN $ids RETURN s.id,t.id,type(r) LIMIT 1500', {'ids': ids})]
        return {'nodes': nodes, 'edges': edges}

    def graph(self, workspace_id, limit=300):
        return self._subgraph(workspace_id, [n['id'] for n in self.nodes(workspace_id, limit=limit)])

    def paths(self, workspace_id, source_id, target_id, max_hops=4):
        hops = max(1, min(int(max_hops), 4))
        rows = self._query(workspace_id, f'MATCH p=(s {{id: $s}})-[*1..{hops}]-(t {{id: $t}}) RETURN [n IN nodes(p) | n.id], [r IN relationships(p) | type(r)] LIMIT 12', {'s': source_id, 't': target_id})
        return [{'nodes': r[0], 'edges': r[1]} for r in rows]

    def neighborhood(self, workspace_id, node_id, hops=2):
        hops = max(1, min(int(hops), 3))
        rows = self._query(workspace_id, f'MATCH (s {{id: $id}})-[*0..{hops}]-(n) RETURN DISTINCT n.id LIMIT 150', {'id': node_id})
        return self._subgraph(workspace_id, [r[0] for r in rows])

    def retrieve(self, workspace_id, query, limit=20):
        limit = max(1, min(int(limit), 40))
        stop = {'the','and','what','which','who','was','with','this','that','could','explain','previous','from','have','does','into','about','affected','system'}
        terms = list(dict.fromkeys(t for t in re.findall(r'[a-z0-9.]+', query.lower()) if len(t) > 2 and t not in stop))[:16]
        if not terms:
            return {'nodes': [], 'edges': [], 'paths': []}
        rows = self._query(workspace_id, 'MATCH (n) WHERE n.kind IN $kinds AND any(term IN $terms WHERE toLower(coalesce(n.label, "") + " " + coalesce(n.text, "")) CONTAINS term) RETURN n ORDER BY n.updated_at DESC LIMIT 12', {'terms': terms, 'kinds': ['Memory', 'Evidence', 'Entity', 'Decision']})
        roots = [self._node(r[0])['id'] for r in rows]
        if not roots:
            return {'nodes': [], 'edges': [], 'paths': []}
        # Actual bounded traversals: semantic links only, avoiding session/run hubs.
        rels = 'MENTIONS|RELATES_TO|SUPPORTS|DEPENDS_ON|OWNED_BY|AFFECTS|RESOLVED_BY'
        paths = self._query(workspace_id, f'MATCH p=(s)-[:{rels}*1..3]-(n) WHERE s.id IN $ids RETURN [x IN nodes(p) | x.id], [r IN relationships(p) | type(r)] LIMIT 80', {'ids': roots})
        ids = list(dict.fromkeys(roots + [i for row in paths for i in row[0]]))[:limit]
        result = self._subgraph(workspace_id, ids)
        allowed = set(ids)
        result['paths'] = [{'nodes': row[0], 'edges': row[1]} for row in paths if all(i in allowed for i in row[0])][:24]
        return result

    def seed(self, workspace_id):
        entries = [
            ('workspace', 'Workspace', 'AcmeShop · synthetic', 'Synthetic incident investigation workspace.'),
            ('checkout-api', 'Entity', 'Checkout API', 'AcmeShop Checkout API processes purchases and uses Redis sessions.'),
            ('release-2-4', 'Entity', 'Release 2.4', 'Synthetic release 2.4 deployed a Redis TTL configuration change before checkout failures.'),
            ('redis-change', 'Evidence', 'Redis TTL configuration change', 'Release 2.4 reduced Redis session TTL from 3600 to 60 seconds. Checkout sessions may expire mid-purchase; correlation is not proof of cause.'),
            ('maya-chen', 'Entity', 'Maya Chen · system owner', 'Maya Chen owns the Checkout API and is the escalation contact.'),
            ('incident-current', 'Entity', 'Checkout incident', 'Synthetic checkout session-expired errors increased after release 2.4.'),
            ('incident-previous', 'Evidence', 'Previous checkout incident INC-104', 'Earlier checkout failures followed an overly short Redis session TTL. Incident review documented the configuration and recovery.'),
            ('previous-resolution', 'Evidence', 'INC-104 documented resolution', 'Earlier lesson: restore Redis session TTL to 3600 seconds, invalidate stale test sessions, monitor checkout completion, and add a TTL regression check before releases.'),
        ]
        for id, kind, label, text in entries:
            if self.get_node(workspace_id, id) is None:
                self.put_node(workspace_id, kind, {'id': id, 'label': label, 'text': text, 'synthetic': True, 'source': 'AcmeShop synthetic demo fixture'})
        for s, t, rel in [('workspace','checkout-api','MENTIONS'),('release-2-4','redis-change','GENERATED'),('redis-change','checkout-api','AFFECTS'),('release-2-4','checkout-api','AFFECTS'),('checkout-api','maya-chen','OWNED_BY'),('incident-current','checkout-api','AFFECTS'),('redis-change','incident-current','RELATES_TO'),('incident-previous','checkout-api','AFFECTS'),('incident-previous','previous-resolution','RESOLVED_BY'),('previous-resolution','redis-change','RELATES_TO'),('redis-change','release-2-4','SUPPORTS')]:
            self.link(workspace_id, s, t, rel)
        return self.graph(workspace_id)
